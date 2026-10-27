"""Reconcile executed evidence, run acceptance checks, and write a QA record."""
import hashlib
import json
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path

import nbformat
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw
from course_pipeline import file_sha, metrics, choose_threshold

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/validation"
OUT.mkdir(parents=True, exist_ok=True)
run = Path((OUT / "smoke_run_path.txt").read_text(encoding="utf-8"))
status = json.loads((run / "run_status.json").read_text())
assert status["status"] == "complete" and status["completed_runs"] == status["planned_runs"] == 30
assert json.loads((run / "config/resolved_config.json").read_text())["code_sha256"] == file_sha(ROOT / "scripts/course_pipeline.py")
result = subprocess.run([sys.executable, str(ROOT / "scripts/check_course_pipeline.py")],
    cwd=ROOT, text=True, encoding="utf-8", capture_output=True,
    env={**os.environ, "PYTHONIOENCODING": "utf-8"})
(OUT / "acceptance_checks.log").write_text(result.stdout + result.stderr, encoding="utf-8")
assert result.returncode == 0, result.stdout + result.stderr
test_count = int(re.search(r"Ran (\d+) tests", result.stderr + result.stdout).group(1))

# Independent artifact integrity: every output hash and the saved ZIP contents.
manifest = json.loads((run / "output_manifest.json").read_text())
for relative, sha in manifest.items(): assert file_sha(run / relative) == sha, relative
with zipfile.ZipFile(run.parent / "deepneoag_smoke_results.zip") as bundle:
    assert bundle.testzip() is None
    for relative, sha in manifest.items():
        assert hashlib.sha256(bundle.read("smoke/" + relative)).hexdigest() == sha, relative

# Recompute every reported test metric from peptide-level evidence.
table = pd.read_csv(run / "tables/test_metrics.csv")
predictions = pd.read_csv(run / "tables/test_predictions.csv")
locks = json.loads((run / "config/locked_selection.json").read_text())["models"]
assert set(locks) == {f"M{i}" for i in range(8)}
checks = 0
for _, row in table.iterrows():
    frame = predictions.loc[predictions.family.eq(row.family)] if row.aggregation == "ensemble" else pd.read_csv(run / "tables" / f"{row.family}_test_predictions_raw.csv")
    if row.aggregation != "ensemble": frame = frame.loc[frame.seed.eq(row.seed)]
    observed = metrics(frame.label, frame.probability, row.threshold)
    for key, value in observed.items(): assert np.isclose(value, row[key], atol=1e-10), (row.family, key)
    checks += 1
for family, lock in locks.items():
    oof = pd.read_csv(run / "tables" / f"{lock['config_id']}_oof.csv")
    assert len(oof) == 256 and oof.id.is_unique
    assert np.isclose(choose_threshold(oof.label.values, oof.probability.values), lock["threshold"])
events = [json.loads(line) for line in (run / "logs/events.jsonl").read_text().splitlines()]
locked_event = next(i for i, event in enumerate(events) if event["event"] == "selection_locked")
assert all(i > locked_event for i, e in enumerate(events) if e["event"] == "trial_complete" and "_final_" in e.get("run", ""))

nb = nbformat.read(OUT / "DeepNeoAG_smoke_executed.ipynb", as_version=4)
nbformat.validate(nb)
errors = [o for c in nb.cells if c.cell_type == "code" for o in c.get("outputs", []) if o.output_type == "error"]
images = [o for c in nb.cells if c.cell_type == "code" for o in c.get("outputs", []) if "image/png" in o.get("data", {})]
assert not errors and len(images) == 8
assert (OUT / "DeepNeoAG_smoke_preview.html").stat().st_size > 100_000
assert "data:image/png;base64" in (OUT / "DeepNeoAG_smoke_preview.html").read_text(encoding="utf-8")

outline = (ROOT / "docs/PRESENTATION_OUTLINE.md").read_text(encoding="utf-8")
assert len(re.findall(r"^## Slide \d+", outline, re.M)) == 18
assert not re.search(r"\b(smoke|checkpoint|resume)\b|Save Version|Original Paper", outline, re.I)
times = re.findall(r"^## Slide .*\((\d+):(\d+)\)", outline, re.M)
assert sum(int(m) * 60 + int(s) for m, s in times) == 1080

paths = sorted((run / "figures").glob("*.png"))
canvas = Image.new("RGB", (2000, 650 * ((len(paths) + 1) // 2)), "white")
for i, path in enumerate(paths):
    picture = Image.open(path).convert("RGB"); picture.thumbnail((980, 605))
    x = i % 2 * 1000 + (1000 - picture.width) // 2; y = i // 2 * 650 + 30
    canvas.paste(picture, (x, y)); ImageDraw.Draw(canvas).text((i % 2 * 1000 + 10, i // 2 * 650 + 8), path.name, fill="black")
canvas.save(OUT / "figure_contact_sheet.png")
receipt = dict(status="passed", smoke_run=str(run), trials=30, model_families=8,
    acceptance_checks=test_count, metric_rows_recomputed=checks, output_files_verified=len(manifest),
    notebook_image_outputs=len(images), presentation_slides=18, presentation_seconds=1080,
    dataset_zip_sha256=file_sha(ROOT / "dist/deepneoag-course-dataset.zip"),
    notebook_sha256=file_sha(ROOT / "notebooks/DeepNeoAG_Course_Project_Kaggle.ipynb"),
    environment=json.loads((run / "config/environment.json").read_text()),
    full_gpu_execution="Not run; user executes full mode on Kaggle.")
(OUT / "validation_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: v for k, v in receipt.items() if k != "environment"}, indent=2))
