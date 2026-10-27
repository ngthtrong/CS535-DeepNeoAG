"""Audit the supplied full run without retraining or changing its evidence.

Run from any directory with the project virtual environment. Writes derived
evidence to outputs/full_analysis; never writes inside results_full.
"""
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (average_precision_score, roc_auc_score,
                            confusion_matrix, matthews_corrcoef)

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "results_full"
OUT = ROOT / "outputs/full_analysis"
OUT.mkdir(parents=True, exist_ok=True)


def read(name):
    return pd.read_csv(RUN / "tables" / (name + ".csv"))


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def calculate(y, p, threshold):
    y, p = np.asarray(y), np.asarray(p)
    tn, fp, fn, tp = confusion_matrix(y, p >= threshold, labels=[0, 1]).ravel()
    precision = tp / (tp + fp) if tp + fp else 0.
    recall = tp / (tp + fn)
    specificity = tn / (tn + fp)
    return dict(ap=average_precision_score(y, p), roc_auc=roc_auc_score(y, p),
                mcc=matthews_corrcoef(y, p >= threshold), precision=precision,
                recall=recall, specificity=specificity,
                f1=2 * tp / (2 * tp + fp + fn), accuracy=(tp + tn) / len(y),
                balanced_accuracy=(recall + specificity) / 2,
                tn=tn, fp=fp, fn=fn, tp=tp, threshold=threshold)


def threshold_fast(y, p):
    """Independent cumulative-confusion implementation of the locked policy."""
    y, p = np.asarray(y, dtype=int), np.asarray(p, dtype=float)
    candidates = np.unique(np.r_[0., .5, p, np.nextafter(p.max(), np.inf)])
    order = np.argsort(p, kind="stable")
    positions = np.searchsorted(p[order], candidates, side="left")
    positives_before = np.r_[0, np.cumsum(y[order])][positions]
    tp = y.sum() - positives_before
    fp = len(y) - positions - tp
    fn = y.sum() - tp
    tn = len(y) - y.sum() - fp
    denom = np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn), dtype=float)
    scores = np.divide(tp * tn - fp * fn, denom, out=np.zeros(len(tp)), where=denom != 0)
    ties = candidates[np.isclose(scores, scores.max(), atol=1e-12, rtol=0)]
    return sorted(ties, key=lambda t: (abs(t - .5), -t))[0]


def bootstrap_values(y, p, threshold, indices):
    """Frequency-weighted exact AP/AUC, including tied scores, for each resample."""
    y, p = np.asarray(y, dtype=int), np.asarray(p, dtype=float)
    order = np.argsort(-p, kind="stable")
    end = np.r_[np.flatnonzero(np.diff(p[order]) != 0), len(y) - 1]
    pred = p >= threshold
    values = []
    for idx in indices:
        weights = np.bincount(idx, minlength=len(y))[order]
        tp_curve = np.cumsum(weights * y[order])[end]
        fp_curve = np.cumsum(weights * (1 - y[order]))[end]
        precision = np.divide(tp_curve, tp_curve + fp_curve,
                              out=np.zeros(len(end)), where=(tp_curve + fp_curve) > 0)
        ap = np.sum(np.diff(np.r_[0, tp_curve]) * precision) / y.sum()
        # Trapezoidal ROC area with a (0,0) origin and grouped tied scores.
        auc = np.sum(np.diff(np.r_[0, fp_curve]) *
                     (tp_curve + np.r_[0, tp_curve[:-1]]) / 2) / (y.sum() * (len(y) - y.sum()))
        yy, pp = y[idx], pred[idx]
        tp = np.sum((yy == 1) & pp); fp = np.sum((yy == 0) & pp)
        fn = y.sum() - tp; tn = len(y) - y.sum() - fp
        den = math.sqrt(float((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)))
        values.append([ap, auc, (tp * tn - fp * fn) / den if den else 0.])
    return np.asarray(values)


def main():
    status = json.loads((RUN / "run_status.json").read_text())
    assert status["status"] == "complete" and status["mode"] == "full"
    plan = json.loads((RUN / "config/planned_runs.json").read_text())
    assert len(plan) == len(set(plan)) == status["completed_runs"] == status["planned_runs"] == 258
    manifest = json.loads((RUN / "output_manifest.json").read_text())
    missing, mismatch = [], []
    for relative, expected in manifest.items():
        path = RUN / relative
        if not path.exists(): missing.append(relative)
        elif sha(path) != expected: mismatch.append(relative)
    assert not mismatch, mismatch
    print(f"Manifest checked: {len(manifest)-len(missing)} present, {len(missing)} absent", flush=True)
    train = pd.read_csv(RUN / "data_audit/train_used.csv")
    test = pd.read_csv(RUN / "data_audit/test_used.csv")
    assert len(train) == 5608 and train.label.sum() == 241
    assert len(test) == 1404 and test.label.sum() == 61
    for name, frame in [("train", train), ("test", test)]:
        original = pd.read_csv(ROOT / "data" / (name + ".csv"))
        pd.testing.assert_frame_equal(frame, original)
        assert frame.id.is_unique and not frame.isna().any().any()
        assert frame.length.eq(frame.sequence.str.len()).all()
        assert frame.sequence.map(lambda s: set(s) <= set("ACDEFGHIKLMNPQRSTVWY") and 0 < len(s) <= 35).all()
    assert pd.concat([train, test]).sequence.is_unique
    assert set(train.id).isdisjoint(test.id)
    assignments = pd.read_csv(RUN / "data_audit/fold_assignments.csv")
    for fold, frame in assignments.groupby("fold"):
        assert len(frame) == len(train) and frame.id.is_unique and set(frame.id) == set(train.id)
        assert set(frame.role) == {"fit", "early_stop", "outer_validation"}
    assert assignments[assignments.role.eq("outer_validation")].id.value_counts().eq(1).all()
    locks = json.loads((RUN / "config/locked_selection.json").read_text())["models"]
    assert set(locks) == {f"M{i}" for i in range(8)}
    cv = read("cv_summary")
    metric_rows = 0
    for run_id in plan:
        folder = RUN / "runs" / run_id
        result = json.loads((folder / "result.json").read_text())
        predictions = pd.read_csv(folder / "predictions.csv")
        assert sha(folder / "predictions.csv") == result["predictions_sha256"]
        expected_ids = test.id if result["final"] else assignments.loc[
            assignments.fold.eq(result["fold"]) & assignments.role.eq("outer_validation"), "id"]
        assert predictions.id.is_unique and set(predictions.id) == set(expected_ids)
        reference = (test if result["final"] else train).set_index("id").loc[predictions.id]
        assert np.array_equal(reference.label, predictions.label)
        for key, value in calculate(predictions.label, predictions.probability, .5).items():
            assert np.isclose(value, result[key], atol=1e-10, rtol=1e-7), (run_id, key)
        metric_rows += 1
    all_pred = read("test_predictions")
    metrics = read("test_metrics")
    for _, row in metrics.iterrows():
        frame = all_pred[all_pred.family.eq(row.family)] if row.aggregation == "ensemble" else read(row.family + "_test_predictions_raw")
        if row.aggregation != "ensemble": frame = frame[frame.seed.eq(row.seed)]
        for key, value in calculate(frame.label, frame.probability, row.threshold).items():
            assert np.isclose(value, row[key], atol=1e-10, rtol=1e-7), (row.family, row.policy, key)
    for _, row in cv.iterrows():
        runs = read(row.config_id + "_cv")
        assert np.isclose(runs.ap.mean(), row.mean_ap)
        assert np.isclose(runs.ap.std(ddof=1), row.std_ap)
    learning, fold_rows = [], []
    for family, lock in locks.items():
        options = cv[cv.family.eq(family)]
        tied = options[options.mean_ap.max() - options.mean_ap <= 1e-6]
        selected = tied.sort_values(["mean_mcc", "trainable_parameters", "config_id"], ascending=[False, True, True]).iloc[0]
        assert selected.config_id == lock["config_id"]
        oof = read(lock["config_id"] + "_oof")
        raw = read(lock["config_id"] + "_oof_raw")
        assert oof.id.is_unique and set(oof.id) == set(train.id)
        expected = raw.groupby("id").probability.mean().reindex(oof.id)
        assert np.allclose(oof.probability, expected, atol=1e-8)
        assert np.isclose(threshold_fast(oof.label, oof.probability), lock["threshold"], atol=1e-10)
        runs = read(lock["config_id"] + "_cv")
        if lock["config"]["kind"] == "cnn":
            assert math.ceil(runs.best_epoch.median()) == lock["refit_epochs"]
            learning.append(dict(family=family, min_best_epoch=int(runs.best_epoch.min()),
                                 median_best_epoch=float(runs.best_epoch.median()), max_best_epoch=int(runs.best_epoch.max()),
                                 refit_epochs=lock["refit_epochs"]))
        for fold, frame in runs.groupby("fold"):
            fold_rows.append(dict(family=family, fold=fold, mean_ap=frame.ap.mean(), seed_sd=frame.ap.std()))
        final_raw = read(family + "_test_predictions_raw")
        ensemble = all_pred[all_pred.family.eq(family)].set_index("id")
        expected = final_raw.groupby("id").probability.mean().reindex(ensemble.index)
        assert np.allclose(ensemble.probability, expected, atol=1e-8)
        assert np.array_equal(ensemble.prediction, ensemble.probability >= lock["threshold"])
    events = [json.loads(s) for s in (RUN / "logs/events.jsonl").read_text().splitlines()]
    locked = next(i for i, e in enumerate(events) if e["event"] == "selection_locked")
    assert all(i > locked for i, e in enumerate(events) if e["event"] == "trial_complete" and "_final_" in e.get("run", ""))
    assert not [e for e in events if e["event"] in ("stage_failed", "trial_failed")]
    print(f"Recomputed {metric_rows} per-run rows, {len(metrics)} test rows and 8 locked thresholds", flush=True)
    # Same stratified resamples across models allow a paired difference analysis.
    # Recreate saved intervals as well; no thresholds or model settings are changed.
    first = all_pred[all_pred.family.eq("M0")]
    ids = first.id.tolist(); y = first.label.to_numpy()
    groups = [np.flatnonzero(y == k) for k in (0, 1)]
    rng = np.random.default_rng(535)
    indices = np.array([np.r_[rng.choice(groups[0], len(groups[0]), replace=True),
                             rng.choice(groups[1], len(groups[1]), replace=True)] for _ in range(2000)])
    ci_saved = read("test_confidence_intervals")
    bootstrap = {}
    for family, lock in locks.items():
        p = all_pred[all_pred.family.eq(family)].set_index("id").loc[ids].probability.to_numpy()
        for policy, threshold in [("fixed_0.5", .5), ("oof_selected", lock["threshold"])]:
            values = bootstrap_values(y, p, threshold, indices)
            for j, metric in enumerate(["ap", "roc_auc", "mcc"]):
                expected = ci_saved[ci_saved.family.eq(family) & ci_saved.policy.eq(policy) & ci_saved.metric.eq(metric)].iloc[0]
                assert np.allclose(np.quantile(values[:, j], [.025, .975]), [expected.lower, expected.upper], atol=1e-7), (family, policy, metric)
            if policy == "oof_selected": bootstrap[family] = values
    pairs = []
    final = metrics[metrics.aggregation.eq("ensemble") & metrics.policy.eq("oof_selected")].set_index("family")
    for a, b in [("M7", "M1"), ("M7", "M4"), ("M4", "M1")]:
        for j, metric in enumerate(["ap", "roc_auc", "mcc"]):
            low, high = np.quantile(bootstrap[a][:, j] - bootstrap[b][:, j], [.025, .975])
            pairs.append(dict(comparison=a + " - " + b, metric=metric, difference=final.loc[a, metric] - final.loc[b, metric],
                              lower=low, upper=high, repetitions=2000,
                              interpretation="Exploratory paired stratified bootstrap; fixed trained models and OOF thresholds; no multiplicity correction"))
    pd.DataFrame(pairs).to_csv(OUT / "paired_test_differences.csv", index=False)
    pd.DataFrame(learning).to_csv(OUT / "learning_summary.csv", index=False)
    pd.DataFrame(fold_rows).to_csv(OUT / "fold_summary.csv", index=False)
    errors = all_pred[all_pred.error_type.ne("correct")].copy()
    errors["confidence_of_error"] = np.where(errors.error_type.eq("FP"), errors.probability, 1-errors.probability)
    errors = errors.sort_values(["family", "error_type", "confidence_of_error", "id"], ascending=[True, True, False, True])
    errors.groupby(["family", "error_type"], sort=False).head(2).to_csv(OUT / "representative_errors.csv", index=False)
    length_rows = []
    for (family, length), frame in all_pred.groupby(["family", "length"]):
        length_rows.append(dict(family=family, length=length, n=len(frame), positives=int(frame.label.sum()),
                                fp=int(frame.error_type.eq("FP").sum()), fn=int(frame.error_type.eq("FN").sum())))
    pd.DataFrame(length_rows).to_csv(OUT / "errors_by_length.csv", index=False)
    code_match = sha(ROOT / "scripts/course_pipeline.py") == json.loads((RUN / "config/resolved_config.json").read_text())["code_sha256"]
    receipt = dict(status="passed_with_provenance_caveat" if not code_match else ("passed" if not missing else "passed_with_missing_artifacts"), reviewed_on="2026-10-25",
                   source="results_full", planned_runs=258, per_run_metric_rows_recomputed=metric_rows,
                   test_metric_rows_recomputed=len(metrics), bootstrap_interval_rows_recomputed=len(ci_saved),
                   configurations_reconciled=len(cv), locked_thresholds_recomputed=8,
                   manifest_files_verified=len(manifest)-len(missing), missing_manifest_files=missing,
                   hash_mismatches=mismatch, source_code_hash_matches=code_match,
                   recorded_code_sha256=json.loads((RUN / "config/resolved_config.json").read_text())["code_sha256"],
                   current_code_sha256=sha(ROOT / "scripts/course_pipeline.py"),
                   scope="Artifact reconciliation and source inspection; does not reproduce GPU training or independently validate similarity filtering.")
    (OUT / "validation_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2), flush=True)
    print(pd.DataFrame(pairs).to_string(index=False))


if __name__ == "__main__":
    main()
