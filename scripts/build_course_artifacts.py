"""Build the validated Kaggle dataset ZIP and standalone notebook."""
import csv
import hashlib
import json
import re
import zipfile
from collections import Counter
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]


def build_dataset():
    data = ROOT / "data"
    for name, counts in [("train", {0: 5367, 1: 241}), ("test", {0: 1343, 1: 61})]:
        with (data / f"{name}.csv").open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        assert Counter(int(r["label"]) for r in rows) == counts
        for r in rows:
            assert r["split"] == name and int(r["length"]) == len(r["sequence"])
            source = (data / "raw" / r["source_file"]).read_text().splitlines()
            assert source[0] == ">" + r["id"] and "".join(source[1:]).strip() == r["sequence"]
    readme = """# DeepNeoAG course dataset

7,012 peptides: 5,608 published training records (241 positive) and 1,404
independent test records (61 positive). Label 1 = neoantigen; 0 = other.
Columns: id,sequence,label,split,length,source_file. Preserve the test split.

Source: https://github.com/B1607/DeepNeoAG
Commit: 0bebb4ff3fa2bc9ba05e51a18771a14ac8b1c897
Reference: Chuang et al. (2024), DOI 10.1016/j.ijbiomac.2024.136252.

Each FASTA is preserved byte-for-byte. Source authors report similarity
filtering at 30%; this package does not recompute similarity. One negative
test peptide (sgh_sequence7831) has length 35 despite the table heading <35.
There are no exact sequence duplicates or train/test sequence overlaps.
Raw sequence length is 11–35. No HLA/MHC annotations are inferred from length.
The other-peptide class is not a guarantee of a perfect biological negative.
This is the final curated dataset, not the initial 32,877-record collection.

Upload this ZIP as a private Kaggle Dataset and attach it to the course
notebook. Kaggle extracts the archive; files are available under its Input.
No PLM weights or precomputed embeddings are included. Internet is required
for the first encoder download. checksums.sha256 covers all packaged files
except the checksum manifest itself. Notebook instructions are delivered
separately in docs/KAGGLE_RUN_GUIDE.md.
"""
    files = {name: (data / name).read_bytes() for name in ["train.csv", "test.csv", "all.csv", "dataset_summary.json"]}
    files["README.md"] = readme.encode("utf-8")
    files["source_file_manifest.json"] = (data / "raw/file_manifest.json").read_bytes()
    files["raw/UPSTREAM_README.md"] = (data / "raw/UPSTREAM_README.md").read_bytes()
    for p in sorted((data / "raw/fasta").rglob("*.fasta")):
        files[p.relative_to(data).as_posix()] = p.read_bytes()
    assert len([n for n in files if n.endswith(".fasta")]) == 7012
    hashes = {name: hashlib.sha256(content).hexdigest() for name, content in files.items()}
    files["checksums.sha256"] = "".join(f"{sha}  {name}\n" for name, sha in sorted(hashes.items())).encode()
    dist = ROOT / "dist"; dist.mkdir(exist_ok=True)
    target = dist / "deepneoag-course-dataset.zip"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        for name, content in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 25, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED; z.writestr(info, content)
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        for name, sha in hashes.items(): assert hashlib.sha256(z.read(name)).hexdigest() == sha
    print(f"Dataset verified: {target}, {target.stat().st_size:,} bytes, {len(files)} files")


def build_notebook():
    md = nbf.v4.new_markdown_cell; code = nbf.v4.new_code_cell
    nb = nbf.v4.new_notebook()
    nb.metadata.update(kernelspec={"display_name": "Python 3", "language": "python", "name": "python3"},
                       language_info={"name": "python", "version": "3.11"})
    nb.cells = [md("""# DeepNeoAG: Learning Through Controlled Experiments

An end-to-end experiment notebook: composition → one-hot MCNN → frozen ESM pooled → single-window CNN → MCNN; then controlled ablations and an 8M/35M encoder comparison.

**Goal:** explain what each modeling choice contributes, not manufacture a winning result.

**Before running:** attach the course dataset ZIP as a Kaggle Dataset; enable Internet. Default is **smoke**, a pipeline check with no scientific conclusions. Use a GPU and change `RUN_MODE` to `full` for the research run, then **Save Version → Save & Run All**. Operations are documented separately from the presentation.

Full protocol: shared 5-fold training CV; separate inner early-stopping data; three neural seeds; configuration/threshold locking; published independent test. No synthetic data or labels are substituted.

The summary and conclusions are produced after execution; no full-run result is prefilled.
"""), md("## Configuration"), code('''RUN_MODE = "smoke"  # "smoke" or "full"
DATASET_DIR = None  # e.g. "/kaggle/input/deepneoag-course-dataset"
RESUME_DIR = None  # optional previously saved output, containing smoke/ or full/
OUTPUT_DIR = "/kaggle/working/deepneoag_results" if __import__("pathlib").Path("/kaggle").exists() else "outputs/deepneoag_results"
BUDGET_HOURS = 10
'''), md("## Environment setup\nInstall FAIR ESM if missing. Use the Kaggle-provided PyTorch GPU installation; do not replace it with a CPU wheel. Exact runtime versions are saved."), code('''import importlib.util, subprocess, sys
if importlib.util.find_spec("esm") is None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "fair-esm==2.0.0"])
''')]
    source = (ROOT / "scripts/course_pipeline.py").read_text(encoding="utf-8")
    source = source.replace('COURSE_CODE_HASH = "development"',
        'COURSE_CODE_HASH = "' + hashlib.sha256(source.encode("utf-8")).hexdigest() + '"')
    sections = re.split(r"^# SECTION: (.+)\n", source, flags=re.M)
    for i in range(1, len(sections), 2):
        title, body = sections[i], sections[i + 1]
        nb.cells += [md(f"### Implementation: {title}\nReusable implementation; the execution sections below explain each research step."), code(body.strip())]
    nb.cells += [md("## Data: provenance, integrity and evaluation partitions\n**Question:** can we trust the labels and preserve independent evaluation?\n**Controlled decisions:** retain published splits, validate sequences, use shared folds. **Evidence:** audit JSON, fold assignment CSV and dataset plots."),
        code('''project = CourseProject(RUN_MODE, DATASET_DIR, RESUME_DIR, OUTPUT_DIR, BUDGET_HOURS)
project.stage("data_validation", project.load_data)
project.stage("data_exploration", project.explore)
'''), md("## Representations: composition, one-hot and contextual ESM features\n**Question:** how much information is available before downstream CNN training? Both ESM models are frozen. Residue vectors exclude BOS/EOS; padded positions are excluded from pooling. Feature IDs, layer, checksum and extraction cost are saved. Caches store float16 and training uses float32, identically on first and resumed runs."),
        code('project.stage("feature_extraction", project.prepare_features)'),
        md("""## Baselines and controlled experiments

| Family | Representation and classifier | Research question |
|---|---|---|
| M0 | Composition + balanced LR | Is amino-acid composition sufficient? |
| M1 | One-hot MCNN | What can supervised sequence-pattern learning achieve? |
| M2/M5 | ESM 8M/35M mean-pooled + LR | What is available in contextual representations? |
| M3/M6 | ESM 8M/35M single-window CNN | Does local extraction add useful information? |
| M4/M7 | ESM 8M/35M MCNN | Are multiple scales complementary? |

**Controlled changes:** LR C; 8M single windows 2/3/4/5/8; MCNN filters 32/64/128/256; weighted/unweighted loss at 64 filters. 35M uses the 8M-selected downstream CNN architecture. Separate fixed-default and tuned comparisons are exported.

**Protocol:** CV splits use seed 535, neural initializations 535/536/537. Early stopping uses only an inner 15% split. LR fits the complete outer-training portion because it has no early stopping. Selection uses mean outer-fold AP, then MCC at 0.5, fewer parameters and configuration ID. Selection scores are not unbiased post-tuning estimates.

**Interpretation:** composition vs one-hot changes classifier as well as representation; MCNN may have more capacity; encoder size also changes embedding dimension. These are limitations, not causal proof.
"""), code('project.stage("cross_validation_and_ablations", project.experiments)'),
        md("## Lock configurations and OOF thresholds\n**Question:** what can be selected without inspecting test results? For each family, average seed probabilities per OOF record and maximize MCC. Also retain the fixed 0.5 threshold. Refit epochs use the ceiling of the median CV best epoch."),
        code('project.stage("selection_lock", project.lock_selection)'),
        md("## Final training\nFit the locked configurations on all published training records. There is no test-driven early stopping. Neural seeds are retrained independently."),
        code('project.stage("final_training", project.final_training)'),
        md("## Independent evaluation and error analysis\n**Evidence:** ensemble and individual-seed metrics, predictions, raw confusion counts, FP/FN examples, and stratified bootstrap 95% intervals. AP is Average Precision, not trapezoidal PR area. Seed SD and bootstrap intervals describe different uncertainties."),
        code('project.stage("independent_evaluation", project.evaluate_test)'),
        md("## Results, figures and takeaways\nGenerate plots from saved evidence. Smoke figures are explicitly marked. Full conclusions must be based on observed outputs. Classifier scores do not prove presentation, immune response or clinical efficacy."),
        code('project.stage("figures_and_interpretation", project.make_plots)'),
        md("## Export and execution status\nA complete status requires all planned trials and final artifacts. A partial run exports existing evidence for resumption; errors preserve the traceback. See the output ZIP and `run_status.json`."),
        code('''project.stage("completion", project.finish)
project.export_archive()  # includes the final stage-end event and final timing table
from IPython.display import display, FileLink
display(FileLink(str(project.root.parent / f"deepneoag_{RUN_MODE}_results.zip")))
print((project.root / "run_status.json").read_text())
'''), md("""## References and limitations

- Dataset and methodological reference: Chuang et al. (2024), https://doi.org/10.1016/j.ijbiomac.2024.136252 ; https://github.com/B1607/DeepNeoAG .
- ESM implementation and model specifications: https://github.com/facebookresearch/esm .
- Kaggle execution and outputs: https://www.kaggle.com/docs/notebooks .
- Similarity filtering is reported by the source, not independently recomputed here. Exact duplicate checks are insufficient to establish low homology.
- There is no MHC/HLA annotation in the supplied CSV. Do not infer MHC type from peptide length.
- The held-out test remains small (61 positives); report uncertainty and avoid claims of broad clinical generalization.
""")]
    nbf.validate(nb)
    out = ROOT / "notebooks/DeepNeoAG_Course_Project_Kaggle.ipynb"; out.parent.mkdir(exist_ok=True)
    nbf.write(nb, out)
    print(f"Standalone notebook: {out} ({len(nb.cells)} cells)")


if __name__ == "__main__":
    build_dataset()
    build_notebook()
