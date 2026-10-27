"""Redraw saved full-run evidence with descriptive labels; no model execution."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import precision_recall_curve, roc_curve, average_precision_score
from model_labels import MODEL_NAMES

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "results_full"
DEST = ROOT / "docs/assets/full_results"
COLORS = dict(zip(MODEL_NAMES, ["#6b7280", "#156b8a", "#ca7512", "#2c8b57", "#7852a0", "#bc482f", "#987836", "#c23c85"]))
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False,
                     "svg.fonttype": "none", "axes.titlepad": 14})
INDEX = []


def read(name):
    return pd.read_csv(RUN / "tables" / f"{name}.csv")


def save(fig, name, caption):
    for ext in ("png", "svg"):
        fig.savefig(DEST / f"{name}.{ext}", dpi=300, bbox_inches="tight", facecolor="white")
    INDEX.append(dict(id=name, file=f"{name}.png", caption=caption, source="results_full/tables"))
    # SVG text remains inspectable: verify no machine family code is displayed.
    import re
    svg = (DEST / f"{name}.svg").read_text(encoding="utf-8")
    assert not re.search(r">[^<>]*\bM[0-7]\b[^<>]*<", svg), name
    plt.close(fig)


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    summary = read("cv_summary").set_index("config_id")
    selected = read("selected_models")
    cv = summary.loc[selected.config_id].reset_index()
    labels = [MODEL_NAMES[f] for f in cv.family]
    positions = np.arange(len(cv))
    fig, ax = plt.subplots(figsize=(11, 6), layout="constrained")
    ax.barh(positions, cv.mean_ap, xerr=cv.std_ap, color=[COLORS[f] for f in cv.family], capsize=4)
    ax.set(yticks=positions, yticklabels=labels, xlim=(0, 1), xlabel="CV Average Precision",
           title="Selected configurations: mean AP and descriptive SD")
    ax.invert_yaxis()
    save(fig, "V11_cv_comparison", "CV used for selection. Error bars: sample SD over fold/seed rows, not a confidence interval.")

    folds = read("selected_cv_runs")
    fig, ax = plt.subplots(figsize=(11, 6), layout="constrained")
    for i, f in enumerate(MODEL_NAMES):
        vals = folds[folds.family.eq(f)].ap.to_numpy()
        ax.scatter(vals, i + np.linspace(-.16, .16, len(vals)), color=COLORS[f], s=30)
    ax.set(yticks=positions, yticklabels=[MODEL_NAMES[f] for f in MODEL_NAMES], xlim=(0, 1),
           xlabel="Outer-validation AP", title="Variation across folds and initializations")
    ax.invert_yaxis()
    save(fig, "V11_fold_seed", "Each point is one run; seeds and folds are correlated, not independent datasets.")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), layout="constrained")
    locks = json.loads((RUN / "config/locked_selection.json").read_text())["models"]
    for f in ("M1", "M3", "M4", "M7"):
        # Explicit fold 0 / seed 535; do not depend on filesystem enumeration.
        h = pd.read_csv(RUN / "runs" / f"{locks[f]['config_id']}_fold0_seed535" / "history.csv")
        for ax, col in zip(axes, ["train_loss", "stop_ap"]):
            ax.plot(h.epoch, h[col], "o-", markersize=3, color=COLORS[f], label=MODEL_NAMES[f])
    axes[0].set(title="Representative fitting histories", xlabel="Epoch", ylabel="Training loss (weights differ)")
    axes[1].set(title="Early-stopping subset", xlabel="Epoch", ylabel="Average Precision", ylim=(0, 1))
    for ax in axes: ax.legend(fontsize=10)
    save(fig, "V08_learning_curves", "Selected configurations, fold 0 and seed 535. Raw loss scales differ; compare AP for quality.")

    ab = read("ablations")
    panels = [(ab[ab.family.eq("M3")], "window", "ESM 8M + CNN: window size"),
              (ab[ab.family.eq("M4") & ab.weighted], "filters", "ESM 8M + MCNN: filters per branch"),
              (ab[ab.family.eq("M4") & ab.filters.eq(64)], "weighted", "ESM 8M + MCNN: loss at 64 filters")]
    fig, axes = plt.subplots(1, 3, figsize=(17, 5), layout="constrained")
    for ax, (frame, field, title) in zip(axes, panels):
        xlabels = frame[field].map({True: "Weighted", False: "Unweighted"}) if field == "weighted" else frame[field].astype(str)
        ax.bar(xlabels, frame.mean_ap, yerr=frame.std_ap, color="#246d87", capsize=4)
        ax.set(title=title, ylabel="CV Average Precision", ylim=(0, 1))
    save(fig, "V09_ablations", "One-factor 8M ablations. Error bars are descriptive fold/seed SD, not confidence intervals.")

    pred = read("test_predictions")
    test = read("test_metrics")
    test = test[test.aggregation.eq("ensemble") & test.policy.eq("oof_selected")].set_index("family").loc[list(MODEL_NAMES)]
    fig, axes = plt.subplots(1, 2, figsize=(17, 7), layout="constrained")
    for f in MODEL_NAMES:
        frame = pred[pred.family.eq(f)]
        precision, recall, _ = precision_recall_curve(frame.label, frame.probability)
        fpr, tpr, _ = roc_curve(frame.label, frame.probability)
        ap = average_precision_score(frame.label, frame.probability)
        style = "--" if f in ("M5", "M6", "M7") else "-"
        axes[0].step(recall, precision, where="post", color=COLORS[f], linestyle=style, label=f"{MODEL_NAMES[f]}  AP={ap:.3f}")
        axes[1].plot(fpr, tpr, color=COLORS[f], linestyle=style, label=MODEL_NAMES[f])
    prevalence = pred[pred.family.eq("M0")].label.mean()
    axes[0].axhline(prevalence, color="#555555", linestyle=":", label=f"Prevalence = {prevalence:.4f}")
    axes[1].plot([0, 1], [0, 1], ":", color="#555555", label="Random ranking")
    axes[0].set(title="Independent test precision–recall", xlabel="Recall", ylabel="Precision")
    axes[1].set(title="Independent test ROC", xlabel="False positive rate", ylabel="True positive rate")
    for ax in axes:
        ax.set(xlim=(0, 1), ylim=(0, 1.02))
        ax.legend(loc="upper center", bbox_to_anchor=(.5, -.13), fontsize=10, ncol=2)
    save(fig, "V12_test_curves", "Locked models, all 1,404 test records. Neural curves use mean probabilities across three seeds.")

    fig, axes = plt.subplots(2, 4, figsize=(17, 8), layout="constrained")
    for ax, (f, r) in zip(axes.flat, test.iterrows()):
        matrix = np.array([[r.tn, r.fp], [r.fn, r.tp]], dtype=int)
        ax.imshow(matrix, cmap="Blues", vmin=0, vmax=1343)
        for (i, j), val in np.ndenumerate(matrix):
            ax.text(j, i, str(val), ha="center", va="center", fontsize=12,
                    bbox=dict(facecolor="white", alpha=.85, edgecolor="none"))
        ax.set(title=f"{MODEL_NAMES[f]}\nThreshold {r.threshold:.4f}", xticks=[0, 1], yticks=[0, 1], xlabel="Predicted label", ylabel="True label")
    save(fig, "V12_confusion", "Raw counts at locked OOF-selected thresholds. Label 1: neoantigen; label 0: other. Common color scale.")

    costs = cv.set_index("family")
    fig, axes = plt.subplots(1, 2, figsize=(17, 6), layout="constrained", gridspec_kw={"width_ratios": [1, 1.5]})
    for small, large, head in [("M2", "M5", "pooled LR"), ("M3", "M6", "CNN"), ("M4", "M7", "MCNN")]:
        subset = costs.loc[[small, large]]
        axes[0].plot(["8M", "35M"], subset.mean_ap, "o-", color=COLORS[small], label=head)
    axes[0].set(title="Encoder size and selected CV performance", xlabel="Frozen ESM encoder", ylabel="CV Average Precision", ylim=(0, 1))
    axes[0].legend(title="Downstream head")
    fs = ["M2", "M5", "M3", "M6", "M4", "M7"]
    subset = costs.loc[fs]
    axes[1].barh(np.arange(6), subset.mean_training_seconds, color=[COLORS[f] for f in fs])
    for i, (_, r) in enumerate(subset.iterrows()):
        axes[1].text(r.mean_training_seconds+.15, i, f"{int(r.trainable_parameters):,} params", va="center", fontsize=9)
    axes[1].set(yticks=np.arange(6), yticklabels=[MODEL_NAMES[f] for f in fs], xlim=(0, 18),
                title="Downstream fitting time and trainable capacity", xlabel="Mean training seconds per fold/seed")
    axes[1].invert_yaxis()
    save(fig, "V10_encoder_comparison", "8M/35M also change dimension and head capacity. Fit timings exclude encoder extraction and are hardware-specific.")

    counts = read("dataset_counts").set_index("split")
    lengths = read("length_counts")
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), layout="constrained")
    x = np.arange(2)
    for offset, col, color in [(-.18, "Other", "#173b50"), (.18, "Neoantigen", "#cf8128")]:
        axes[0].bar(x+offset, counts.loc[["train", "test"], col], width=.36, label=col, color=color)
    axes[0].set(xticks=x, xticklabels=["Train", "Test"], ylabel="Peptides", title="Published class counts")
    axes[0].legend()
    for label, color in [(0, "#173b50"), (1, "#cf8128")]:
        frame = lengths[lengths.label.eq(label)].groupby("length")["count"].sum()
        axes[1].step(frame.index, frame.values, where="mid", label="Other" if label == 0 else "Neoantigen", color=color)
    axes[1].set(title="Published peptide lengths (train + test)", xlabel="Amino acids", ylabel="Peptides")
    axes[1].legend()
    save(fig, "V04_dataset", "Published class counts and lengths; no biological grouping is inferred from length.")
    pd.DataFrame(INDEX).to_csv(DEST / "figure_index.csv", index=False)
    (DEST / "README.md").write_text("# Full-run figures with descriptive model names\n\nRecreated from saved results using `scripts/redraw_full_figures.py`; no training or metric selection was repeated. PNG: 300 dpi; SVG: editable text. Original run evidence remains in `results_full/`. Captions are in `figure_index.csv`.\n", encoding="utf-8")
    print(f"Redrew {len(INDEX)} figures (PNG + SVG): {DEST}")


if __name__ == "__main__":
    main()
