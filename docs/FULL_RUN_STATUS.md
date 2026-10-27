# Post-full-run completion record

Reviewed 25 October 2026 against `plan.md`. Delivery format: Markdown, as requested.

| Plan requirement | Status | Evidence |
|---|---|---|
| Dataset ZIP, notebook and guides | Previously delivered; retained | Existing `dist/`, `notebooks/`, `docs/VALIDATION.md` |
| Full execution | Complete in supplied evidence: 258/258 fits, eight families | `results_full/run_status.json`; unique planned IDs |
| Reconcile predictions/metrics | Complete | 258 run rows, 52 test rows, 22 CV configurations, eight thresholds and 48 CI rows |
| Supplied artifact integrity | Complete | 1,580/1,580 manifest files match SHA-256 |
| Process, results and conclusions report | Complete | `docs/FULL_RESULTS_REPORT.md` |
| Insert real results into outline and notes | Complete | `docs/PRESENTATION_OUTLINE.md`; `FULL_RESULTS_SLIDE_MAP.md` |
| Update visuals for selected settings | Complete | `docs/VISUAL_ASSET_GUIDE.md`, distinguishing default/selected filters |
| Inspect numerical figures | Contact sheet inspected | `outputs/full_analysis/figure_contact_sheet.png` |
| Exact execution-source identity | Unresolved provenance gap | Recorded code hash differs from current source/notebook; exact executed full notebook is absent from supplied artifacts |

Numerical evidence is suitable for the course report **with the stated provenance and statistical caveats**. Previously recorded implementation acceptance checks do not prove identity of the executable used for the full run. This review does not rerun GPU training or reconstruct similarity filtering.

The practical remaining handoff is to recover the executed notebook/source from the Kaggle version that generated these outputs and archive it beside the run. This session has no established Kaggle connection or saved executed full notebook. Do not reconstruct that provenance by relabelling the different current source.

Scientific follow-up remains proposed: reproducible sequence clustering and grouped validation, an external cohort, parameter-matched heads and training-only calibration. These require new evidence and experiments. After changes informed by the present test, evaluation requires another untouched cohort.

Re-run checks with `scripts/analyze_full_results.py`; regenerate the report with `scripts/write_full_report.py`. Original `results_full/` artifacts remain unchanged. The new receipt and derived CSV files are in `outputs/full_analysis/`.
