# Validation Record

Reviewed on **2026-10-25**. The original sections below record implementation validation. Full research findings are now in [FULL_RESULTS_REPORT.md](FULL_RESULTS_REPORT.md); full artifact reconciliation is recorded separately below and in [FULL_RUN_STATUS.md](FULL_RUN_STATUS.md).

## Supplied full-run reconciliation

`results_full/` reports 258/258 completed fits covering eight model families. `scripts/analyze_full_results.py` independently recomputes 258 run metric rows, 52 test metric rows, eight OOF-selected thresholds, 22 configuration summaries and 48 saved bootstrap interval rows. It verifies split membership, original CSV equality, prediction IDs/labels, seed-ensemble means, selection rules, refit epochs and lock ordering. All 1,580 listed output files match manifest SHA-256 hashes. Derived evidence is saved in `outputs/full_analysis/` without changing the original run.

The figure contact sheet was inspected for visible labels, legends and clipping. The 18-slide outline now contains full results, with negative findings and uncertainty preserved. Its planned duration remains 1,080 seconds.

**Provenance qualification:** full-run `code_sha256` is `3bd6cb69a8bfeca0a63bf91c461152c45312a7e5c3b9ff55308d7090009b997e`, while the current source and notebook identify `a01bdafcf50131f31f1cc5bca963e66cfa6f9a6ac4240bbada93a6ec33fcdf95`. The exact executed full notebook/source is not supplied. Numerical reconciliation passes, but this is not a reproduced GPU training run or proof of historical implementation identity. The receipt status is `passed_with_provenance_caveat`.

## Verified deliverables

- `dist/deepneoag-course-dataset.zip`: 2,385,641 bytes; 7,012 FASTA records, train/test/all CSV, English README, source manifest, summary, upstream README and checksums.
- Published counts are preserved: train 5,608 / 241 positives; test 1,404 / 61 positives. The 35-residue test sample is retained.
- Standalone notebook: 38 cells; all code cells parse and notebook format validation passes. The embedded source hash matches the development pipeline.
- Presentation: 18 main slides, exactly 1,080 seconds of planned speaking time, with notes and figure mapping. There is no dedicated paper-comparison or execution-operations section.
- Visual guide: six English Gemini prompts, asset mapping and credit/license records. Both credited reference images were downloaded; source metadata and hashes are under `docs/assets/references/`.

## Clean-kernel execution

The exact notebook logic was executed top-to-bottom in a new local kernel. Only the configured dataset/output paths were adapted for local verification. The dataset was extracted from the actual upload ZIP; its **7,019 checksum entries** were validated by the notebook before modeling.

- Mode: smoke, real biological labels and real frozen ESM-2 8M/35M weights.
- Used samples: 256 train, 64 held-out test; two folds, one initialization, one epoch.
- Completed: **30/30 fits**, covering all eight model families and reduced ablations.
- Final state: `complete`; no notebook error outputs.
- Eight PNG outputs are embedded in the executed notebook; PNG and SVG files were exported.
- The saved HTML preview contains embedded images and can be viewed without a running kernel.
- Figure PNGs and a contact sheet were visually inspected for labels, legends and clipping. This is a local figure review, not a claim of inspection inside Kaggle's UI.

Local environment: Python 3.13, CPU PyTorch 2.14.1, NumPy 2.2.6, pandas 2.2.3, scikit-learn 1.6.1, Matplotlib 3.10.8, FAIR ESM 2.0.0. Exact build strings are recorded in the machine-readable receipt and the run's environment JSON. A Windows application-control failure with pandas 3.1 was resolved by using pandas 2.2.3 in the project virtual environment. No system security settings were changed.

## Acceptance checks

All **16** checks passed:

1. Mean pooling excludes padding.
2. CNN predictions are invariant to changes in padded values; entirely invalid branches remain finite.
3. Known confusion counts and AP agree with a hand-checkable example.
4. OOF threshold maximization and tie policy work as specified.
5. Fit/early-stop/outer-validation partitions are disjoint and do not contain test IDs.
6. Resume rejects incompatible signatures.
7. Interrupting after one epoch and resuming produces exactly the same CPU weights as uninterrupted three-epoch training.
8. Failed stages preserve a traceback and failed state.
9. Budget stops produce partial state and skip later stages.
10. Dataset archive integrity, FASTA count and standalone notebook syntax pass.
11. The full experiment registry contains 9 LR and 13 neural configurations: **258 planned fits** including final refits.
12. Completed trial results are reused without updating the checkpoint; corrupted prediction files are rejected.
13. Explicit parent folders and automatic discovery resolve nested dataset layouts.
14. Missing paths report actual attached directories and visible CSV paths.
15. Multiple compatible datasets require an explicit selection rather than choosing silently.
16. Both train and test CSV schemas are validated during discovery.

Additional reconciliation passed:

- Recomputed **32 test-metric rows** from saved peptide predictions.
- Recomputed each selected OOF threshold; all OOF IDs are unique and complete.
- Confirmed selection-lock events precede all final trial completions.
- Verified all output-file hashes, including the corresponding entries inside the output ZIP; the receipt records the exact count.
- Confirmed the dataset/notebook checksums in the validation receipt match the current deliverables.

## Evidence locations

- Executed notebook: [`outputs/validation/DeepNeoAG_smoke_executed.ipynb`](../outputs/validation/DeepNeoAG_smoke_executed.ipynb)
- HTML preview: [`outputs/validation/DeepNeoAG_smoke_preview.html`](../outputs/validation/DeepNeoAG_smoke_preview.html)
- Acceptance log: [`outputs/validation/acceptance_checks.log`](../outputs/validation/acceptance_checks.log)
- Machine-readable receipt: [`outputs/validation/validation_receipt.json`](../outputs/validation/validation_receipt.json)
- Figure contact sheet: [`outputs/validation/figure_contact_sheet.png`](../outputs/validation/figure_contact_sheet.png)
- Latest verified run: the path recorded in `outputs/validation/smoke_run_path.txt`.
- Its result archive: `deepneoag_smoke_results.zip` in the parent directory of that run.

The `outputs/` directory is local validation evidence and is excluded from version control. It is not required by the uploaded notebook. Keep the receipt/log if archiving project evidence elsewhere.

## Not yet executed

The **full five-fold, three-seed GPU study has not been run**. Full mode intentionally requires a GPU; the user will execute it on Kaggle. No full-result claims, winning-model statements or final numeric slide conclusions are supplied.

GPU checkpoint continuation, Kaggle platform output preservation and full-run timing have not been validated in an actual Kaggle session. The local deterministic continuation check covers CPU behavior; GPU determinism remains conditional on the runtime/hardware, with algorithm warnings enabled. Review the saved version and run status after full execution.

## Reproduce verification

From the project root, with the course environment installed:

```powershell
.\.venv\Scripts\python.exe scripts/build_course_artifacts.py
.\.venv\Scripts\python.exe scripts/run_notebook_smoke.py
.\.venv\Scripts\python.exe scripts/record_validation.py
```

Rebuilding changes notebook metadata IDs and may change its file checksum; regenerate the receipt after rebuilding. Changes to pipeline code require a fresh signature/output directory, selected automatically by the local smoke runner's code-hash suffix.
