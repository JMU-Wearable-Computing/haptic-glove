from pathlib import Path
import sys
p = Path(__file__).resolve().parent / "Sammy_MOCAP_Raw"
# ensure the extractor module directory is on sys.path
sys.path.insert(0, str(p))
from extract_markers import extract_marker_positions

for raw in sorted(p.glob("*_Raw.csv")):
    out = p / (raw.stem + "_Processed.csv")
    print(f"Processing {raw.name} -> {out.name}")
    extract_marker_positions(str(raw), output_csv=str(out))
print('Done')
