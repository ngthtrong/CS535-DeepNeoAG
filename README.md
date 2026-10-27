# DeepNeoAG Course Project

An English-language, reproducible course project about controlled peptide-classification experiments. The emphasis is the research process, including baselines, contextual embeddings, CNN architecture, imbalance, validation and error analysis.

## Deliverables

- **Upload to Kaggle:** [dataset ZIP](dist/deepneoag-course-dataset.zip).
- **Import as a Kaggle notebook:** [standalone notebook](notebooks/DeepNeoAG_Course_Project_Kaggle.ipynb).
- **Run instructions:** [Kaggle guide](docs/KAGGLE_RUN_GUIDE.md).
- **18-slide, 18-minute talk:** [outline and speaker notes](docs/PRESENTATION_OUTLINE.md).
- **Image preparation:** [11 prompts and insertion plan](docs/IMAGE_GENERATION_PROMPTS.md); [visual assets and credits](docs/VISUAL_ASSET_GUIDE.md). New conceptual images await generation and insertion.
- **Methods and experiment definitions:** [experiment protocol](docs/EXPERIMENT_PROTOCOL.md).
- **Acceptance checks and execution evidence:** [validation record](docs/VALIDATION.md).

The default notebook mode is `smoke`. Its outputs verify the pipeline and are not scientific findings. The supplied **complete full run (258 fits)** is now analyzed in the [full Markdown report](docs/FULL_RESULTS_REPORT.md), with [updated presentation notes](docs/PRESENTATION_OUTLINE.md), a [slide evidence map](docs/FULL_RESULTS_SLIDE_MAP.md) and [post-run status](docs/FULL_RUN_STATUS.md). ESM 35M + MCNN has the highest observed test AP (0.5758), but the difference from one-hot MCNN is uncertain. The recorded full-run source hash differs from the current source/notebook, a provenance limitation documented in the report. Set `RUN_MODE="full"` on Kaggle with a GPU for a new full experiment.

The supplied train/test split is preserved: 5,608 training records and 1,404 independent test records. Five core approaches are investigated, with an additional frozen ESM-2 35M comparison. There is no encoder fine-tuning and no synthetic-data fallback.

## Development and rebuilding

Use Python 3.11+ (local verification uses 3.13). Install a suitable PyTorch build for your machine and `requirements-course.txt` in a virtual environment. The notebook installs only missing FAIR ESM and uses Kaggle's installed GPU PyTorch.

```powershell
.\.venv\Scripts\python.exe scripts/build_course_artifacts.py
.\.venv\Scripts\python.exe scripts/check_course_pipeline.py
.\.venv\Scripts\python.exe scripts/run_notebook_smoke.py
```

`scripts/course_pipeline.py` is the development source embedded directly in the notebook. Rebuild after editing it. The uploaded notebook does not import any workspace script. An executed verification copy and HTML preview are saved under `outputs/validation/`.

## Sources

- Chuang et al. (2024), DOI: https://doi.org/10.1016/j.ijbiomac.2024.136252
- Author dataset: https://github.com/B1607/DeepNeoAG , commit `0bebb4ff3fa2bc9ba05e51a18771a14ac8b1c897`
- ESM: https://github.com/facebookresearch/esm
- Kaggle notebooks: https://www.kaggle.com/docs/notebooks

Dataset-specific provenance and the 35-residue boundary case are documented in `data/README.md` and the dataset ZIP README. No exact-match overlap does not establish the absence of sequence-similarity leakage.
