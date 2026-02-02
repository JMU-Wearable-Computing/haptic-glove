#!/usr/bin/env python3
"""Combined data processing utility

- Extract marker X/Y/Z + Time from raw multi-row-header CSVs (from
  `extract_markers.py`).
- Generate small Python modules exposing processed CSV columns as NumPy
  arrays (from `vars_from_processed.py`).

Usage examples:
  python Python/data_processing.py process path/to/_Raw.csv
  python Python/data_processing.py gen-vars path/to/_Processed.csv
  python Python/data_processing.py regenerate --dir Python/Sammy_MOCAP_Raw --gen-vars
"""
from pathlib import Path
import csv
import re
import argparse
import pandas as pd
from typing import List, Optional, Dict, Tuple
import glob


def _find_frame_header_row(path: str, max_lines: int = 200) -> int:
    with open(path, newline='') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if not row:
                continue
            first = str(row[0]).strip()
            if first == 'Frame' or first.startswith('Frame'):
                return i
            if i >= max_lines:
                break
    raise ValueError("Could not find 'Frame' header row in the first %d lines" % max_lines)


def extract_marker_positions(csv_path: str, output_csv: Optional[str] = None) -> pd.DataFrame:
    header_row = _find_frame_header_row(csv_path)
    header_rows_raw = []
    with open(csv_path, newline='') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i <= header_row:
                header_rows_raw.append([c if c != '' else '' for c in row])
            else:
                break

    ncols = len(header_rows_raw[-1])
    normalized = []
    for r in header_rows_raw:
        if len(r) < ncols:
            r = r + [''] * (ncols - len(r))
        elif len(r) > ncols:
            r = r[:ncols]
        normalized.append(r)

    tuples = []
    for j in range(ncols):
        tup = tuple(normalized[i][j] for i in range(len(normalized)))
        tuples.append(tup)

    data = pd.read_csv(csv_path, header=None, skiprows=header_row + 1)
    # align data columns
    if data.shape[1] != ncols:
        if data.shape[1] > ncols:
            data = data.iloc[:, :ncols]
        else:
            for _ in range(ncols - data.shape[1]):
                data[data.shape[1]] = pd.NA

    df = data
    df.columns = pd.MultiIndex.from_tuples(tuples)

    columns = df.columns
    keep_cols: List = []
    for col in columns:
        if isinstance(col, tuple):
            lower_levels = [str(s).lower() for s in col if s is not None]
            last = str(col[-1])
        else:
            lower_levels = [str(col).lower()]
            last = str(col)

        is_marker = any('marker' in s for s in lower_levels)
        is_xyz = last in ('X', 'Y', 'Z')
        if is_marker and is_xyz:
            keep_cols.append(col)

    if not keep_cols:
        for col in columns:
            last = col[-1] if isinstance(col, tuple) else col
            if str(last) in ('X', 'Y', 'Z'):
                keep_cols.append(col)

    # Ensure Time column is included
    for col in columns:
        levels = list(col) if isinstance(col, tuple) else [col]
        for lev in levels:
            try:
                if isinstance(lev, str) and 'time' in lev.lower():
                    if col not in keep_cols:
                        keep_cols.append(col)
                    break
            except Exception:
                continue

    result = df.loc[:, keep_cols].copy()

    def _flatten(col):
        levels = list(col) if isinstance(col, tuple) else [col]
        parts = []
        for p in levels:
            if p is None:
                continue
            s = str(p).strip()
            if s == '':
                continue
            s = s.replace(' ', '_').replace('(', '').replace(')', '')
            parts.append(s)
        if not parts:
            return ''
        return '_'.join(parts)

    flat_names = [_flatten(c) for c in result.columns]

    # Drop capture-start/time columns robustly
    drop_indices = []
    for i, col in enumerate(result.columns):
        levels = col if isinstance(col, tuple) else (col,)
        for l in levels:
            s = str(l).lower()
            if 'capture_start_time' in s.replace(' ', '_') or ('capture' in s and 'start' in s and 'time' in s):
                drop_indices.append(i)
                break

    if drop_indices:
        cols_to_drop = [result.columns[i] for i in drop_indices]
        result = result.drop(columns=cols_to_drop)
        flat_names = [n for j, n in enumerate(flat_names) if j not in drop_indices]

    time_idx = None
    for i, name in enumerate(flat_names):
        if 'time' in name.lower():
            time_idx = i
            flat_names[i] = 'Time'
            break

    if time_idx is not None and time_idx != 0:
        cols = list(result.columns)
        cols.insert(0, cols.pop(time_idx))
        result = result.loc[:, cols]
        flat_names.insert(0, flat_names.pop(time_idx))

    result.columns = flat_names

    if output_csv:
        result.to_csv(output_csv, index=False)
    return result


def _sanitize(name: str) -> str:
    s = str(name).strip()
    s = re.sub(r"[^0-9a-zA-Z_]", "_", s)
    s = re.sub(r"_+", "_", s)
    s = s.strip("_")
    if not s:
        s = "col"
    if re.match(r"^[0-9]", s):
        s = "_" + s
    return s


def make_module_from_csv(csv_path: str, out_module: Optional[str] = None) -> str:
    p = Path(csv_path)
    if not p.exists():
        raise FileNotFoundError(csv_path)

    df = pd.read_csv(p)
    cols = list(df.columns)

    seen = set()
    var_map: List[Tuple[str, str]] = []
    for c in cols:
        cstr = str(c)
        tokens = [t for t in re.split(r'[:_\s]+', cstr) if t]
        while tokens and tokens[0].lower() in ('bone', 'marker', 'sammy'):
            tokens.pop(0)

        coord = None
        if tokens and tokens[-1].upper() in ('X', 'Y', 'Z'):
            coord = tokens.pop(-1).upper()
        if tokens and tokens[-1].lower() == 'position':
            tokens.pop(-1)
        if tokens and re.fullmatch(r'[A-Za-z0-9]{1,2}', tokens[-1]):
            tokens.pop(-1)
        bone_name = '_'.join(tokens) if tokens else cstr
        bone_name = bone_name.replace(':', '_')
        candidate = f"{bone_name}_{coord}" if coord else bone_name
        v = _sanitize(candidate)
        if not v:
            v = _sanitize(cstr)
        base = v
        i = 1
        while v in seen:
            v = f"{base}_{i}"
            i += 1
        seen.add(v)
        var_map.append((v, c))

    if out_module is None:
        out_module = str(p.with_name(p.stem + '_vars.py'))

    out_p = Path(out_module)
    with out_p.open('w', encoding='utf8') as f:
        f.write('# Auto-generated module exposing columns from: {}\n'.format(str(p.name)))
        f.write('import pandas as pd\n')
        f.write('\n')
        f.write("_csv_path = {!r}\n".format(str(p.resolve())))
        f.write('_df = pd.read_csv(_csv_path)\n')
        f.write('\n')
        for var, col in var_map:
            f.write("{var} = _df[{col!r}].values\n".format(var=var, col=col))
        f.write('\n')
        f.write('del _df\n')

    return str(out_p)


def regenerate_all(raw_dir: str, gen_vars: bool = False) -> None:
    p = Path(raw_dir)
    raws = sorted(p.glob('*_Raw.csv'))
    for r in raws:
        out = str(r.with_name(r.stem + '_Processed.csv'))
        print('Processing', r.name, '->', Path(out).name)
        extract_marker_positions(str(r), output_csv=out)
        if gen_vars:
            vm = make_module_from_csv(out)
            print(' Wrote vars module:', vm)
    print('Done')


def _main():
    parser = argparse.ArgumentParser(prog='data_processing')
    sub = parser.add_subparsers(dest='cmd')

    p_proc = sub.add_parser('process', help='Process a single raw CSV to produce _Processed.csv')
    p_proc.add_argument('csv')
    p_proc.add_argument('--out', '-o', help='output processed CSV path')

    p_vars = sub.add_parser('gen-vars', help='Generate vars module for a processed CSV')
    p_vars.add_argument('csv')
    p_vars.add_argument('--out', '-o', help='output module path')

    p_reg = sub.add_parser('regenerate', help='Process all *_Raw.csv in a directory')
    p_reg.add_argument('--dir', default='Python/Sammy_MOCAP_Raw')
    p_reg.add_argument('--gen-vars', action='store_true')

    args = parser.parse_args()
    if args.cmd == 'process':
        in_path = Path(args.csv)
        if not in_path.exists():
            raise SystemExit(f'Input file not found: {in_path}')
        outp = args.out if args.out else str(in_path.with_name(in_path.stem + '_Processed.csv'))
        extract_marker_positions(str(in_path), output_csv=outp)
        print('Wrote processed marker positions to:', outp)
    elif args.cmd == 'gen-vars':
        in_path = Path(args.csv)
        if not in_path.exists():
            raise SystemExit(f'Input file not found: {in_path}')
        outm = args.out if args.out else None
        mod = make_module_from_csv(str(in_path), out_module=outm)
        print('Wrote module:', mod)
    elif args.cmd == 'regenerate':
        regenerate_all(args.dir, gen_vars=args.gen_vars)
    else:
        parser.print_help()


if __name__ == '__main__':
    _main()
