import csv
from typing import List, Optional

import pandas as pd


def _find_frame_header_row(path: str, max_lines: int = 50) -> int:
    """Return the zero-based index of the header row that starts with 'Frame'."""
    with open(path, newline='') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if not row:
                continue
            first = row[0].strip()
            if first == 'Frame' or first.startswith('Frame'):
                return i
            if i >= max_lines:
                break
    raise ValueError("Could not find 'Frame' header row in the first %d lines" % max_lines)


def extract_marker_positions(csv_path: str, output_csv: Optional[str] = None) -> pd.DataFrame:
    """
    Load a motion-capture CSV and return only the X/Y/Z position columns for bone markers,
    preserving the original CSV labels (MultiIndex column headers).

    Behavior:
    - Detects the header block by locating the row that begins with 'Frame'.
    - Loads the CSV with a MultiIndex header composed of all rows up to that 'Frame' row.
    - Selects columns where any header level contains the word 'marker' (case-insensitive)
      and the final header level is one of 'X','Y','Z'.
    - Returns a DataFrame with the same MultiIndex columns. If `output_csv` is given,
      the result is written to that path (the multi-row header is preserved).

    Example:
        df = extract_marker_positions('Sammy_LatPulls_1_Raw.csv')

    """
    header_row = _find_frame_header_row(csv_path)
    # read header rows manually to allow uneven row lengths, then read data
    header_rows_raw = []
    with open(csv_path, newline='') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i <= header_row:
                header_rows_raw.append([c if c != '' else '' for c in row])
            else:
                break

    ncols = len(header_rows_raw[-1])
    # normalize lengths of each header row to ncols
    normalized = []
    for r in header_rows_raw:
        if len(r) < ncols:
            r = r + [''] * (ncols - len(r))
        elif len(r) > ncols:
            r = r[:ncols]
        normalized.append(r)

    # build tuples for column MultiIndex
    tuples = []
    for j in range(ncols):
        tup = tuple(normalized[i][j] for i in range(len(normalized)))
        tuples.append(tup)

    # read data rows into DataFrame and assign the MultiIndex columns
    data = pd.read_csv(csv_path, header=None, skiprows=header_row + 1)
    if data.shape[1] != ncols:
        # try to trim or pad data columns to match header length
        if data.shape[1] > ncols:
            data = data.iloc[:, :ncols]
        else:
            # pad with NaN columns
            for _ in range(ncols - data.shape[1]):
                data[data.shape[1]] = pd.NA

    df = data
    df.columns = pd.MultiIndex.from_tuples(tuples)

    # If columns are not MultiIndex (single header), normalize to tuples for uniform handling
    columns = df.columns
    # Build a list of boolean keep flags
    keep_cols: List = []
    for col in columns:
        # col may be a tuple (MultiIndex) or a single label
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
        # Fallback: select any columns whose last header is X/Y/Z (in case 'marker' token missing)
        for col in columns:
            last = col[-1] if isinstance(col, tuple) else col
            if str(last) in ('X', 'Y', 'Z'):
                keep_cols.append(col)

    # Ensure Time column is included (match any header level containing 'time')
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

    # Flatten column names to single-level strings for clearer output and to ensure
    # the Time column is easy to find. Build sanitized names from MultiIndex levels.
    def _flatten(col):
        levels = list(col) if isinstance(col, tuple) else [col]
        parts = []
        for p in levels:
            if p is None:
                continue
            s = str(p).strip()
            if s == '':
                continue
            # remove problematic characters and normalize spaces
            s = s.replace(' ', '_').replace('(', '').replace(')', '')
            parts.append(s)
        if not parts:
            return ''
        return '_'.join(parts)

    # Build flattened names for columns
    flat_names = [_flatten(c) for c in result.columns]

    # Remove unwanted Capture_Start_Time columns (any header level contains this)
    drop_indices = []
    for i, col in enumerate(result.columns):
        levels = col if isinstance(col, tuple) else (col,)
        for l in levels:
            s = str(l).lower()
            # match both 'capture_start_time' and 'capture start time' variants
            if 'capture_start_time' in s.replace(' ', '_') or ('capture' in s and 'start' in s and 'time' in s):
                drop_indices.append(i)
                break

    if drop_indices:
        cols_to_drop = [result.columns[i] for i in drop_indices]
        result = result.drop(columns=cols_to_drop)
        # remove corresponding flattened names
        flat_names = [n for j, n in enumerate(flat_names) if j not in drop_indices]

    # If any flattened name contains 'Time', move that column to the front and
    # rename it to 'Time' (preserve units in parentheses removed).
    time_idx = None
    for i, name in enumerate(flat_names):
        if 'time' in name.lower():
            time_idx = i
            flat_names[i] = 'Time'
            break

    # reorder so Time is first (if found)
    if time_idx is not None and time_idx != 0:
        cols = list(result.columns)
        cols.insert(0, cols.pop(time_idx))
        result = result.loc[:, cols]
        flat_names.insert(0, flat_names.pop(time_idx))

    result.columns = flat_names

    if output_csv:
        result.to_csv(output_csv, index=False)
    return result


if __name__ == '__main__':
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description='Extract bone marker X/Y/Z positions from CSV')
    parser.add_argument('csv', help='input CSV path')
    parser.add_argument('--out', '-o', help='optional output CSV path')
    args = parser.parse_args()

    in_path = Path(args.csv)
    if not in_path.exists():
        raise SystemExit(f'Input file not found: {in_path}')

    out_path = None
    if args.out:
        out_path = args.out
    else:
        out_path = str(in_path.with_name(in_path.stem + '_Processed.csv'))

    # Run extraction and write output
    extract_marker_positions(str(in_path), output_csv=out_path)
    print(f'Wrote processed marker positions to: {out_path}')
