# Kaggle Run Guide

## 1. Upload and attach the dataset

1. Create a **private Kaggle Dataset** and upload `dist/deepneoag-course-dataset.zip`.
2. Create a notebook by importing `notebooks/DeepNeoAG_Course_Project_Kaggle.ipynb`.
3. Add the dataset through the Input panel. Kaggle extracts supported ZIP uploads.
4. Enable Internet for FAIR ESM installation and official model downloads. Select a GPU for the full run. One GPU is used; a dual-GPU accelerator does not automatically double speed.

Start with `DATASET_DIR = None`: the notebook searches attached inputs recursively for a compatible `train.csv` / `test.csv` pair. Dataset display titles are not reliable filesystem paths. Copy the mounted path from the Input panel if selecting explicitly; do not infer it from the displayed title. An explicit path may be the exact data folder or a parent folder in the updated notebook. Multiple compatible datasets require an exact selection. Do not edit source labels or published splits.

If you see `found 0 compatible datasets`, run this independent diagnostic cell:

```python
from pathlib import Path
input_root = Path("/kaggle/input")
print("Attached directories:")
for p in sorted(input_root.iterdir()):
    print(p)
print("\nFolders containing train.csv:")
for p in sorted(input_root.rglob("train.csv")):
    print(p.parent, "test.csv:", (p.parent / "test.csv").is_file())
```

Set `DATASET_DIR = None` or paste one of the printed folders exactly, preserving case. If no `train.csv` is printed, check that the dataset contains extracted CSV files rather than only the ZIP, or that the correct dataset is attached. Then rerun the configuration cell and the cell that constructs `project` (or Run All); the failed project instance must not be reused.

## 2. Check the pipeline

Keep `RUN_MODE="smoke"` and run all cells. This uses actual sequences and both pretrained encoders with reduced samples/epochs/folds. It verifies execution and export; its metric values are not research evidence.

Expected outputs under `/kaggle/working/deepneoag_results/smoke/` include `run_status.json`, figures, histories, predictions and checkpoints. The sibling `deepneoag_smoke_results.zip` contains the export. Check that status is `complete` and there is no traceback.

## 3. Execute full experiments

Change only the configuration as needed:

```python
RUN_MODE = "full"
DATASET_DIR = None
RESUME_DIR = None
OUTPUT_DIR = "/kaggle/working/deepneoag_results"
BUDGET_HOURS = 10
```

Use **Save Version → Save & Run All**. This starts in a clean execution session; do not rely on variables or downloads from an interactive session. The notebook installs missing FAIR ESM, creates features, evaluates configurations, locks selection, refits, evaluates test and exports figures without manual stage selection.

Allow the version to finish. Download the saved output ZIP and the executed `.ipynb`. The full matrix contains 258 fits; runtime depends on GPU, stopping epochs, downloads and storage. The first smoke timing is not a reliable linear estimate of the complete run.

The notebook logs the actual Python/library/GPU environment. It does not replace Kaggle's CUDA PyTorch. FAIR ESM is pinned to 2.0.0; official FAIR checkpoints may contain argparse.Namespace, which is narrowly allowlisted for safe PyTorch loading. Local resume checkpoints contain optimizer/RNG state and are loaded as trusted project artifacts; only resume your own outputs.

## 4. Resume a partial run

1. Save the partial version's outputs and attach them as an Input to the same notebook.
2. Keep the same mode and experiment settings.
3. Set `RESUME_DIR` to the folder containing `full/config/signature.json`, or directly to its `full` directory.
4. Run a new Save & Run All.

The program validates the experiment/data signature, copies caches and checkpoints to writable output, skips verified completed runs, and resumes incomplete neural trials at the next epoch. If a feature extraction was interrupted before its cache was committed, that encoder's extraction starts again. Within a version, extraction batches are logged; completed encoder caches are retained.

Do not point full mode to smoke output. Signature mismatch stops the run rather than silently reusing a different experiment. `BUDGET_HOURS` is a per-session runtime control and does not change the experiment signature.

At the budget boundary, the current epoch finishes and existing evidence is exported with `partial` status. A failed trial produces `failed` and `logs/error.txt`; it is not silently omitted. Abrupt platform termination may prevent the final ZIP from being written, but incrementally written files/checkpoints are still the resume source if Kaggle preserves them. Output saving remains subject to platform limits; check the saved version.

## 5. Find evidence for slides

| Need | File |
|---|---|
| Dataset description | `data_audit/audit.json`, `tables/dataset_counts.csv` |
| Fold membership and early stopping | `data_audit/fold_assignments.csv` |
| Actual tried configurations | `config/experiment_registry.json` |
| Fixed defaults comparison | `tables/fixed_configuration_comparison.csv` |
| CV/tuning | `tables/cv_summary.csv`, `tables/ablations.csv` |
| Per-epoch learning | `tables/all_epoch_history.csv`, `runs/*/history.csv` |
| OOF predictions | `tables/*_oof.csv`, `tables/*_oof_raw.csv` |
| Frozen choices | `config/locked_selection.json` |
| Test table and uncertainty | `tables/test_metrics.csv`, `tables/test_confidence_intervals.csv` |
| Individual peptide errors | `tables/error_analysis.csv` |
| Encoder extraction cost | `tables/encoder_costs.csv` |
| Slide-ready evidence | `presentation/`, `figures/` |

Only use output with `mode=full` and `status=complete` for final research claims. Keep negative results and unstable folds visible; do not select only favorable runs.

## 6. Troubleshooting

- **Dataset not found/ambiguous:** inspect the Input tree and set the exact dataset folder.
- **GPU missing:** full intentionally fails; enable an accelerator. CPU is supported for smoke.
- **Internet/model download failure:** enable Internet and retry. No fake embedding fallback is used.
- **Out of memory:** retry after freeing GPU memory. If changing batch size or architecture, use a fresh experiment/output directory and record the change; do not mix signatures.
- **Partial after 10 hours:** attach the saved output and resume. Do not reduce the research matrix silently.
- **Different settings or source code:** rebuild the notebook and use a fresh output directory. Existing cache/checkpoint compatibility must not be assumed.

Kaggle reference: https://www.kaggle.com/docs/notebooks ; dataset reference: https://www.kaggle.com/docs/datasets .
