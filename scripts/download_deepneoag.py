"""Download the authors' pinned peptide dataset and preserve its published splits."""

import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
COMMIT = "0bebb4ff3fa2bc9ba05e51a18771a14ac8b1c897"
REPOSITORY = "https://github.com/B1607/DeepNeoAG"
ARCHIVE_URL = f"https://codeload.github.com/B1607/DeepNeoAG/zip/{COMMIT}"
EXPECTED = {("train", 0): 5367, ("train", 1): 241,
            ("test", 0): 1343, ("test", 1): 61}
FIELDS = ["id", "sequence", "label", "split", "length", "source_file"]


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "CS535-DeepNeoAG-dataset"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def main():
    raw = DATA / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    archive = raw / f"DeepNeoAG_{COMMIT}.zip"
    if not archive.exists():
        print("Downloading pinned author archive...", flush=True)
        content = fetch(ARCHIVE_URL)
        if not zipfile.is_zipfile(io.BytesIO(content)):
            raise ValueError("Downloaded response is not a ZIP archive")
        archive.write_bytes(content)
    tree = json.loads(fetch(f"https://api.github.com/repos/B1607/DeepNeoAG/git/trees/{COMMIT}?recursive=1"))
    if tree.get("truncated") or tree["sha"] != COMMIT:
        raise ValueError("Incomplete or unexpected upstream tree")
    entries = {item["path"]: item for item in tree["tree"] if item["type"] == "blob"}
    expected_paths = {path for path in entries if path.startswith("fasta/") and path.endswith(".fasta")}
    rows, manifest, found = [], [], set()
    with zipfile.ZipFile(archive) as bundle:
        for member in bundle.infolist():
            path = PurePosixPath(member.filename)
            relative = PurePosixPath(*path.parts[1:])
            upstream = str(relative)
            if upstream != "README.md" and upstream not in expected_paths:
                continue
            content = bundle.read(member)
            git_hash = hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
            if git_hash != entries[upstream]["sha"]:
                raise ValueError(f"Upstream hash mismatch: {upstream}")
            target = raw / ("UPSTREAM_README.md" if upstream == "README.md" else relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
            manifest.append({"source_file": upstream, "bytes": len(content),
                             "git_blob_sha1": git_hash,
                             "sha256": hashlib.sha256(content).hexdigest()})
            if upstream == "README.md":
                continue
            found.add(upstream)
            parts = relative.parts
            split = {"Train": "train", "Test": "test"}[parts[1]]
            label = {"pos": 1, "neg": 0}[parts[2]]
            lines = [line.strip() for line in content.decode("utf-8-sig").splitlines() if line.strip()]
            if not lines or not lines[0].startswith(">") or sum(line.startswith(">") for line in lines) != 1:
                raise ValueError(f"Expected exactly one FASTA record: {upstream}")
            sequence = "".join(lines[1:])
            if not sequence or not set(sequence) <= set("ACDEFGHIKLMNPQRSTVWY") or len(sequence) > 35:
                raise ValueError(f"Unexpected sequence alphabet/length: {upstream}")
            rows.append({"id": lines[0][1:], "sequence": sequence, "label": label,
                         "split": split, "length": len(sequence), "source_file": upstream})
    if found != expected_paths:
        raise ValueError("Archive is missing expected FASTA files")
    counts = Counter((row["split"], row["label"]) for row in rows)
    if counts != Counter(EXPECTED):
        raise ValueError(f"Counts differ from published split: {counts}")
    rows.sort(key=lambda row: (row["split"], row["label"], row["source_file"]))
    for name, selected in [("train", [r for r in rows if r["split"] == "train"]),
                           ("test", [r for r in rows if r["split"] == "test"]),
                           ("all", rows)]:
        with (DATA / f"{name}.csv").open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(selected)
    groups = defaultdict(list)
    for row in rows:
        groups[row["sequence"]].append(row)
    duplicates = {sequence: records for sequence, records in groups.items() if len(records) > 1}
    overlaps = sorted({r["sequence"] for r in rows if r["split"] == "train"}
                      & {r["sequence"] for r in rows if r["split"] == "test"})
    conflicts = [seq for seq, records in groups.items() if len({r["label"] for r in records}) > 1]
    summary = {
        "repository": REPOSITORY, "commit": COMMIT,
        "archive_url": ARCHIVE_URL,
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
        "total_records": len(rows),
        "counts": {split: {"positive": counts[split, 1], "other": counts[split, 0],
                           "total": counts[split, 0] + counts[split, 1]} for split in ["train", "test"]},
        "length_min": min(r["length"] for r in rows),
        "length_max": max(r["length"] for r in rows),
        "records_not_strictly_shorter_than_35": [r for r in rows if r["length"] >= 35],
        "unique_sequences": len(groups),
        "duplicate_sequence_groups": len(duplicates),
        "duplicate_records_beyond_first": sum(len(v) - 1 for v in duplicates.values()),
        "exact_train_test_sequence_overlap": len(overlaps),
        "conflicting_label_sequences": len(conflicts),
        "all_fasta_git_hashes_verified": True,
        "similarity_filter": "Authors report <30% similarity filtering; not recomputed locally.",
        "label_definition": {"1": "neoantigen (upstream pos)", "0": "other peptide (upstream neg)"},
    }
    (DATA / "dataset_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (DATA / "raw" / "file_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (DATA / "duplicate_sequences.json").write_text(json.dumps(duplicates, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
