"""Inspect all raw datasets and generate outputs/reports/dataset_inventory.md."""

import sys
from datetime import datetime, timezone
from pathlib import Path

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cognitive_graph.paths import DATA_RAW, OUTPUTS
from cognitive_graph.datasets import choices13k, cpc15, cpc18


def _human_size(nbytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if nbytes < 1024:
            return f"{nbytes:.1f} {unit}"
        nbytes /= 1024
    return f"{nbytes:.1f} TB"


def _file_info(path: Path) -> dict:
    if path.exists():
        return {"exists": True, "size": path.stat().st_size}
    return {"exists": False, "size": 0}


def inspect_choices13k(lines: list[str]):
    lines.append("## choices13k\n")
    dir_ = DATA_RAW / "choices13k"
    files = {"c13k_problems.json": None, "c13k_selections.csv": None}

    lines.append("### Files\n")
    lines.append("| File | Size | Rows | Columns |")
    lines.append("|------|------|------|---------|")

    for fname in files:
        info = _file_info(dir_ / fname)
        if not info["exists"]:
            lines.append(f"| {fname} | MISSING | — | — |")
            continue
        files[fname] = info

    try:
        data = choices13k.load()
    except FileNotFoundError as e:
        lines.append(f"\n**Error loading:** {e}\n")
        return

    sel = data["selections"]
    probs = data["problems"]

    lines.append(
        f"| c13k_selections.csv | {_human_size(files['c13k_selections.csv']['size'])} "
        f"| {len(sel)} | {len(sel.columns)} |"
    )
    lines.append(
        f"| c13k_problems.json | {_human_size(files['c13k_problems.json']['size'])} "
        f"| {len(probs)} entries | — |"
    )

    lines.append("\n### Column Names (c13k_selections.csv)\n")
    lines.append(f"`{list(sel.columns)}`\n")

    lines.append("### JSON Structure (c13k_problems.json)\n")
    lines.append(f"- Number of problems: {len(probs)}")
    if probs:
        first = probs[0] if isinstance(probs, list) else next(iter(probs.values()))
        lines.append(f"- Keys per problem: `{list(first.keys())}`")
        lines.append(f"- Example (first entry):\n```json\n{_truncate(first)}\n```\n")

    lines.append("### First rows (c13k_selections.csv)\n")
    lines.append(f"```\n{sel.head(3).to_string()}\n```\n")

    print(f"[choices13k] selections: {len(sel)} rows, {len(sel.columns)} cols")
    print(f"[choices13k] problems: {len(probs)} entries")


def inspect_cpc15(lines: list[str]):
    lines.append("## CPC15\n")
    dir_ = DATA_RAW / "cpc15"
    fnames = [
        "RawDataExperiment1sorted.csv",
        "RawDataExperiment2sorted.csv",
        "RawDataExperiment3.csv",
    ]

    lines.append("### Files\n")
    lines.append("| File | Size | Rows | Columns |")
    lines.append("|------|------|------|---------|")

    try:
        data = cpc15.load()
    except FileNotFoundError as e:
        for fname in fnames:
            info = _file_info(dir_ / fname)
            status = _human_size(info["size"]) if info["exists"] else "MISSING"
            lines.append(f"| {fname} | {status} | — | — |")
        lines.append(f"\n**Error loading:** {e}\n")
        return

    keys = ["exp1", "exp2", "exp3"]
    for fname, key in zip(fnames, keys):
        info = _file_info(dir_ / fname)
        df = data[key]
        lines.append(
            f"| {fname} | {_human_size(info['size'])} | {len(df)} | {len(df.columns)} |"
        )
        print(f"[cpc15/{key}] {len(df)} rows, {len(df.columns)} cols")

    lines.append("\n### Column Names\n")
    for key in keys:
        df = data[key]
        lines.append(f"- **{key}**: `{list(df.columns)}`\n")

    lines.append("### First rows (exp1)\n")
    lines.append(f"```\n{data['exp1'].head(3).to_string()}\n```\n")


def inspect_cpc18(lines: list[str]):
    lines.append("## CPC18\n")
    dir_ = DATA_RAW / "cpc18"

    lines.append("### Files\n")
    lines.append("| File | Size | Rows | Columns |")
    lines.append("|------|------|------|---------|")

    csv_info = _file_info(dir_ / "all_CPC18_raw_data.csv")
    pdf_info = _file_info(dir_ / "CPC18_dictionary.pdf")

    try:
        data = cpc18.load()
    except FileNotFoundError as e:
        lines.append(
            f"| all_CPC18_raw_data.csv | {'MISSING' if not csv_info['exists'] else _human_size(csv_info['size'])} | — | — |"
        )
        lines.append(
            f"| CPC18_dictionary.pdf | {_human_size(pdf_info['size']) if pdf_info['exists'] else 'MISSING'} | — | — |"
        )
        lines.append(f"\n**Error loading:** {e}\n")
        return

    df = data["raw"]
    lines.append(
        f"| all_CPC18_raw_data.csv | {_human_size(csv_info['size'])} | {len(df)} | {len(df.columns)} |"
    )
    lines.append(
        f"| CPC18_dictionary.pdf | {_human_size(pdf_info['size'])} | — (PDF) | — |"
    )

    lines.append("\n### Column Names\n")
    lines.append(f"`{list(df.columns)}`\n")

    lines.append("### First rows\n")
    lines.append(f"```\n{df.head(3).to_string()}\n```\n")

    print(f"[cpc18] {len(df)} rows, {len(df.columns)} cols")


def _truncate(obj, maxlen=500) -> str:
    import json
    s = json.dumps(obj, indent=2)
    if len(s) > maxlen:
        return s[:maxlen] + "\n... (truncated)"
    return s


def main():
    lines = [
        "# Dataset Inventory\n",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n",
    ]

    inspect_choices13k(lines)
    inspect_cpc15(lines)
    inspect_cpc18(lines)

    report_dir = OUTPUTS / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "dataset_inventory.md"
    report_path.write_text("\n".join(lines))
    print(f"\nReport written to: {report_path}")


if __name__ == "__main__":
    main()
