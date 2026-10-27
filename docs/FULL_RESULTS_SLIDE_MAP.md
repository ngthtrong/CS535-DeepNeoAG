# Full-run evidence for the 18-slide talk

The [outline](PRESENTATION_OUTLINE.md) remains 18 slides and 18 minutes. Paths below are relative to the repository root. Numerical assets come from the complete full run. Model predictions and thresholds remain locked.

| Slides | Evidence / asset | What to emphasize |
|---|---|---|
| 1–4 | `docs/EXPERIMENT_PROTOCOL.md`; conceptual V01/V02 | Sequence classification and independent approaches; no clinical claim |
| 5–6 | `results_full/data_audit/audit.json`; `tables/dataset_counts.csv`; `docs/assets/full_results/V04_dataset.png` | Train 5,608/241 positive; test 1,404/61 positive; preserve the length-35 record |
| 7 | `results_full/data_audit/fold_assignments.csv`; `config/locked_selection.json` | Inner stopping versus outer selection; no test-driven setting changes |
| 8 | `Composition + LR [config ace9324f90]`; CV and test tables | C=1; CV AP 0.1287; test AP 0.0714 |
| 9 | `One-hot + MCNN [config 24b1db6137]`; CV and test tables | CV AP 0.4943; test AP 0.5408; 28,801 parameters |
| 10 | `results_full/features/esm_8M.json`; `esm_35M.json` | Frozen layers 6/12; D=320/480 |
| 11 | `ESM 8M + pooled LR [config baec5be73e]`, `ESM 8M + CNN [config 2db43af49f]`, `ESM 8M + MCNN [config aca8787dd7]`; selected models table | C=0.1; window 3; selected MCNN 256 filters; 1,280 concat features |
| 12 | `results_full/config/experiment_registry.json`; `tables/ablations.csv` | 22 settings, 240 CV fits, 18 final refits |
| 13 | `docs/assets/full_results/V08_learning_curves.png`; `tables/encoder_costs.csv`; `outputs/full_analysis/learning_summary.csv` | First-fold/seed curves; extraction and training costs differ |
| 14 | `docs/assets/full_results/V11_cv_comparison.png`; `V11_fold_seed.png`; `outputs/full_analysis/fold_summary.csv` | Descriptive SD and difficult fold; seeds are correlated |
| 15 | `docs/assets/full_results/V09_ablations.png`; `V10_encoder_comparison.png`; `tables/fixed_configuration_comparison.csv` | Weighted AP gain, non-monotonic filters and mixed encoder results |
| 16 | `docs/assets/full_results/V12_test_curves.png`; `tables/test_metrics.csv`; `test_confidence_intervals.csv`; `outputs/full_analysis/paired_test_differences.csv` | ESM 35M + MCNN highest observed AP; intervals do not establish superiority |
| 17 | `outputs/full_analysis/representative_errors.csv`; `validation_receipt.json` | ESM 35M + MCNN FP sgh_sequence7831, FN neo_sequence56; sample and provenance limits |
| 18 | `docs/FULL_RESULTS_REPORT.md`, Sections 5–10 | Strong one-hot baseline; uncertain gains; similarity-aware external evaluation |

Unqualified `tables/`, `config/` and `features/` paths are under `results_full/`. Redrawn numerical figures are under `docs/assets/full_results/`; a bare figure filename in this table refers to that directory. CV and test tables mean `tables/cv_summary.csv` and `tables/test_metrics.csv`; full selected IDs are in `tables/selected_models.csv`. Main test values use `aggregation=ensemble`, `policy=oof_selected`. Label fixed-0.5 and individual-seed values explicitly.

Appendix: all eight confusion panels, complete metrics/intervals, fixed versus tuned settings, seed spread, errors by length and both code hashes. Keep complete axes, legends and denominators when placing figures. Named PNG/SVG exports are under `docs/assets/full_results/`; untouched historical originals remain under `results_full/figures/`.
