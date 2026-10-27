"""Execute the exact deliverable notebook in a clean local Python kernel."""
import json
import os
import sys
import zipfile
import hashlib
from pathlib import Path
import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter

ROOT = Path(__file__).resolve().parents[1]
kernel_root = ROOT / "tmp/jupyter"
kernel_dir = kernel_root / "kernels/deepneoag-course"
kernel_dir.mkdir(parents=True, exist_ok=True)
(kernel_dir / "kernel.json").write_text(json.dumps(dict(
    argv=[sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
    display_name="DeepNeoAG local verification", language="python")), encoding="utf-8")
os.environ["JUPYTER_PATH"] = str(kernel_root)
os.environ["MPLBACKEND"] = "module://matplotlib_inline.backend_inline"
path = ROOT / "notebooks/DeepNeoAG_Course_Project_Kaggle.ipynb"
nb = nbformat.read(path, as_version=4)
code_hash = hashlib.sha256((ROOT / "scripts/course_pipeline.py").read_bytes()).hexdigest()[:10]
verification_output = ROOT / f"outputs/verified_run_{code_hash}"
# Exercise the actual upload ZIP, including its per-file checksum manifest.
dataset = ROOT / "tmp/kaggle_dataset_verification"
dataset.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(ROOT / "dist/deepneoag-course-dataset.zip") as archive:
    archive.extractall(dataset)
for cell in nb.cells:
    if cell.cell_type == "code" and 'RUN_MODE = "smoke"' in cell.source:
        cell.source += "\n# Local verification paths; research configuration is unchanged.\n"
        cell.source += f"DATASET_DIR = {str(dataset)!r}\n"
        cell.source += f"OUTPUT_DIR = {str(verification_output)!r}\n"
client = NotebookClient(nb, timeout=7200, kernel_name="deepneoag-course", resources={"metadata": {"path": str(ROOT)}})
out = ROOT / "outputs/validation"; out.mkdir(parents=True, exist_ok=True)
try:
    client.execute()
finally:
    nbformat.write(nb, out / "DeepNeoAG_smoke_executed.ipynb")
nbformat.validate(nb)
html, _ = HTMLExporter().from_notebook_node(nb)
(out / "DeepNeoAG_smoke_preview.html").write_text(html, encoding="utf-8")
(out / "smoke_run_path.txt").write_text(str(verification_output / "smoke"), encoding="utf-8")
print("Clean-kernel notebook completed; executed notebook and HTML saved:", out)
