"""Create a Python module exporting variables for each column in a processed CSV.

Usage:
  python Python/vars_from_processed.py PATH/TO/Processed.csv
  python Python/vars_from_processed.py PATH/TO/Processed.csv --out my_vars.py

This will write a small module that, when imported, loads the CSV and exposes
one variable per column (NumPy arrays via pandas `.values`). Variable names are
sanitized from the CSV column headers into valid Python identifiers.
"""
from pathlib import Path
import pandas as pd
import re
import argparse
from typing import Dict, List, Tuple


def _sanitize(name: str) -> str:
    s = str(name).strip()
    # replace non-alphanumeric with underscore
    s = re.sub(r"[^0-9a-zA-Z_]", "_", s)
    # collapse multiple underscores
    s = re.sub(r"_+", "_", s)
    # remove leading/trailing underscores
    s = s.strip("_")
    if not s:
        s = "col"
    # prefix if starts with digit
    if re.match(r"^[0-9]", s):
        s = "_" + s
    return s


def make_module_from_csv(csv_path: str, out_module: str = None) -> str:
    """Read `csv_path` and write a Python module at `out_module` (or default).

    Returns the path to the written module.
    """
    p = Path(csv_path)
    if not p.exists():
        raise FileNotFoundError(csv_path)

    df = pd.read_csv(p)
    cols = list(df.columns)

    # build unique sanitized variable names
    seen = set()
    var_map: List[Tuple[str, str]] = []  # (varname, original_column)
    for c in cols:
        cstr = str(c)
        # split into tokens by delimiters
        tokens = [t for t in re.split(r'[:_\s]+', cstr) if t]
        # drop leading descriptors
        while tokens and tokens[0].lower() in ('bone', 'marker', 'sammy'):
            tokens.pop(0)

        coord = None
        # last token X/Y/Z indicates coordinate
        if tokens and tokens[-1].upper() in ('X', 'Y', 'Z'):
            coord = tokens.pop(-1).upper()

        # remove trailing 'Position' token if present
        if tokens and tokens[-1].lower() == 'position':
            tokens.pop(-1)

        # remove trailing short id tokens (like D, 9, 11, 1C)
        # these are typically marker IDs appended to the bone name
        if tokens and re.fullmatch(r'[A-Za-z0-9]{1,2}', tokens[-1]):
            tokens.pop(-1)

        # remaining tokens form the bone name
        bone_name = '_'.join(tokens) if tokens else cstr
        bone_name = bone_name.replace(':', '_')

        if coord:
            candidate = f"{bone_name}_{coord}"
        else:
            candidate = bone_name

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
        # embed absolute CSV path so module works from anywhere
        f.write("_csv_path = {!r}\n".format(str(p.resolve())))
        f.write("_df = pd.read_csv(_csv_path)\n")
        f.write('\n')
        for var, col in var_map:
            # use repr(col) to handle quotes
            f.write("{var} = _df[{col!r}].values\n".format(var=var, col=col))
        f.write('\n')
        f.write('# Cleanup internal reference\n')
        f.write('del _df\n')

    return str(out_p)


def load_into_namespace(csv_path: str, namespace: Dict):
    """Load CSV columns into the provided `namespace` dict using sanitized names.

    Example:
        ns = {}
        load_into_namespace('..._Processed.csv', ns)
        # then use ns['Time'], ns['Bone_Marker_...']
    """
    p = Path(csv_path)
    if not p.exists():
        raise FileNotFoundError(csv_path)
    df = pd.read_csv(p)
    cols = list(df.columns)
    seen = set()
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
        namespace[v] = df[c].values


def _main():
    parser = argparse.ArgumentParser(description='Generate Python module exposing CSV columns as variables')
    parser.add_argument('csv', help='processed CSV path')
    parser.add_argument('--out', '-o', help='output module path (optional)')
    args = parser.parse_args()

    out = make_module_from_csv(args.csv, args.out)
    print('Wrote module:', out)


if __name__ == '__main__':
    _main()
