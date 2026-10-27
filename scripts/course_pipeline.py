"""Development source embedded verbatim into the standalone Kaggle notebook.

The notebook builder divides this module at SECTION markers. No local imports
from this file are required when the notebook is uploaded to Kaggle.
"""
# SECTION: Imports and reproducibility utilities
import copy
import csv
import hashlib
import importlib.metadata
import json
import logging
import math
import os
import pickle
import platform
import random
import shutil
import sys
import time
import traceback
import warnings
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import (accuracy_score, average_precision_score,
    balanced_accuracy_score, confusion_matrix, f1_score, matthews_corrcoef,
    precision_score, recall_score, roc_auc_score, precision_recall_curve, roc_curve)
from torch.utils.data import DataLoader, TensorDataset

COURSE_CODE_HASH = "development"
AA = "ACDEFGHIKLMNPQRSTVWY"
ENCODERS = {"8M": ("esm2_t6_8M_UR50D", 6, 320),
            "35M": ("esm2_t12_35M_UR50D", 12, 480)}
METRIC_NAMES = ["ap", "roc_auc", "mcc", "precision", "recall", "specificity",
                "f1", "accuracy", "balanced_accuracy", "tn", "fp", "fn", "tp"]
FAMILY_COLORS = {"M0": "#6b7280", "M1": "#18354a", "M2": "#2878b5", "M3": "#d78335",
                 "M4": "#167d8d", "M5": "#6baed6", "M6": "#b59b28", "M7": "#8a6fb0"}


def native(value):
    if isinstance(value, dict): return {str(k): native(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [native(v) for v in value]
    if isinstance(value, (np.integer, np.floating)): return value.item()
    if isinstance(value, Path): return str(value)
    return value


def atomic_json(path, obj):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(native(obj), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temp.replace(path)


def atomic_csv(path, frame):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".csv.tmp")
    frame.to_csv(temp, index=False); temp.replace(path)


def digest(obj):
    return hashlib.sha256(json.dumps(native(obj), sort_keys=True).encode()).hexdigest()


def file_sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""): h.update(block)
    return h.hexdigest()


def find_dataset_directory(dataset_dir=None, kaggle_root="/kaggle/input", local_roots=None):
    """Resolve an exact dataset folder or a parent without guessing its title/slug."""
    input_root = Path(kaggle_root)
    explicit = Path(dataset_dir).expanduser() if dataset_dir is not None else None
    roots = [explicit] if explicit is not None else (
        [input_root] if input_root.exists() else
        [Path(p) for p in (local_roots if local_roots is not None else
                          [Path.cwd() / "data", Path.cwd().parent / "data"])])
    required = {"id", "sequence", "label", "split", "length", "source_file"}
    candidates = []; rejected = []
    for root in roots:
        if not root.is_dir(): continue
        directories = [root] + sorted({p.parent for p in root.rglob("train.csv")})
        for folder in dict.fromkeys(directories):
            if not (folder / "train.csv").is_file() or not (folder / "test.csv").is_file(): continue
            try:
                for filename in ["train.csv", "test.csv"]:
                    columns = set(pd.read_csv(folder / filename, nrows=2).columns)
                    if not required <= columns:
                        raise ValueError(f"{filename} missing columns {sorted(required - columns)}")
            except Exception as e:
                rejected.append(f"{folder}: {e}"); continue
            # An exact compatible folder is an intentional, unambiguous selection.
            if explicit is not None and folder.resolve() == explicit.resolve(): return folder.resolve()
            candidates.append(folder.resolve())
    candidates = sorted(set(candidates))
    if len(candidates) == 1: return candidates[0]
    input_dirs = sorted(str(p) for p in input_root.iterdir() if p.is_dir())[:12] if input_root.is_dir() else []
    visible_csvs = sorted(str(p) for p in input_root.rglob("train.csv"))[:12] if input_root.is_dir() else []
    zip_files = sorted({str(p) for root in roots if root.is_dir() for p in root.rglob("*.zip")})[:12]
    reason = f"Found {len(candidates)} compatible dataset folders: {[str(p) for p in candidates]}."
    if explicit is not None and not explicit.is_dir():
        reason = f"DATASET_DIR does not exist or is not a directory: {explicit}. " + reason
    raise ValueError(reason + "\nSearched roots: " + str([str(p) for p in roots])
        + "\nAvailable Kaggle input directories: " + str(input_dirs)
        + "\nVisible train.csv files:\n" + ("\n".join(visible_csvs) or "(none)")
        + "\nRejected CSV pairs: " + str(rejected[:12])
        + "\nZIP files in searched roots: " + str(zip_files)
        + "\nUse DATASET_DIR=None to search attached inputs, or copy the exact folder containing "
          "train.csv and test.csv from the Input panel. The dataset display title may differ from its mounted path. "
          "If only a ZIP is visible, extract/upload its contents so the two CSV files are available.")


def set_seed(seed):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    if torch.cuda.is_available(): torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.use_deterministic_algorithms(True, warn_only=True)


def metrics(y, prob, threshold=0.5):
    y = np.asarray(y, dtype=int); prob = np.asarray(prob, dtype=float)
    if len(np.unique(y)) != 2: raise ValueError("Both labels are required for evaluation")
    if not np.isfinite(prob).all(): raise ValueError("Non-finite prediction")
    pred = prob >= threshold
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return dict(ap=average_precision_score(y, prob), roc_auc=roc_auc_score(y, prob),
        mcc=matthews_corrcoef(y, pred), precision=precision_score(y, pred, zero_division=0),
        recall=recall_score(y, pred), specificity=tn / (tn + fp),
        f1=f1_score(y, pred, zero_division=0), accuracy=accuracy_score(y, pred),
        balanced_accuracy=balanced_accuracy_score(y, pred), tn=int(tn), fp=int(fp),
        fn=int(fn), tp=int(tp), threshold=float(threshold))


def choose_threshold(y, prob):
    """OOF-only selection: best MCC, closest to .5, then larger threshold."""
    candidates = np.unique(np.r_[0., .5, prob, np.nextafter(float(max(prob)), np.inf)])
    scores = np.array([matthews_corrcoef(y, np.asarray(prob) >= t) for t in candidates])
    tied = candidates[np.isclose(scores, scores.max(), atol=1e-12, rtol=0)]
    return float(sorted(tied, key=lambda t: (abs(t - .5), -t))[0])


class BudgetStop(Exception):
    pass


# SECTION: Padding-aware models and feature helpers
class MaskedMCNN(nn.Module):
    def __init__(self, dim, windows, filters, dropout=.3):
        super().__init__(); self.windows = tuple(windows)
        self.convs = nn.ModuleList([nn.Conv1d(dim, filters, k) for k in windows])
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(filters * len(windows), 1)

    def forward(self, x, lengths):
        x = x.transpose(1, 2); blocks = []
        for k, conv in zip(self.windows, self.convs):
            a = F.relu(conv(x))
            valid = torch.arange(a.shape[-1], device=x.device)[None, :] + k <= lengths[:, None]
            pooled = a.masked_fill(~valid[:, None, :], -torch.inf).amax(dim=-1)
            pooled = torch.where(valid.any(1)[:, None], pooled, torch.zeros_like(pooled))
            blocks.append(pooled)
        return self.fc(self.dropout(torch.cat(blocks, dim=1))).squeeze(-1)


def onehot_features(sequences, max_len=35):
    x = np.zeros((len(sequences), max_len, 20), dtype=np.float32)
    indices = {a: i for i, a in enumerate(AA)}
    for i, sequence in enumerate(sequences):
        for j, a in enumerate(sequence): x[i, j, indices[a]] = 1
    return x


def composition_features(sequences):
    return np.array([[s.count(a) / len(s) for a in AA] for s in sequences], dtype=np.float32)


def masked_mean(x, lengths):
    mask = np.arange(x.shape[1])[None, :] < np.asarray(lengths)[:, None]
    return (x * mask[..., None]).sum(1) / np.asarray(lengths)[:, None]


def config_id(c):
    return f"{c['family']}_{digest(c)[:10]}"


def neural_config(family, feature, windows, filters, weighted=True):
    return dict(family=family, kind="cnn", feature=feature, windows=list(windows),
                filters=int(filters), weighted=bool(weighted))


def lr_config(family, feature, c):
    return dict(family=family, kind="lr", feature=feature, C=float(c), weighted=True)


# SECTION: Project setup, logging and data validation
class ProjectCore:
    def __init__(self, mode="smoke", dataset_dir=None, resume_dir=None,
                 output_dir="/kaggle/working/deepneoag_results", budget_hours=10):
        if mode not in ("smoke", "full"): raise ValueError("RUN_MODE must be smoke or full")
        self.mode = mode; self.started = time.monotonic(); self.budget = budget_hours * 3600
        self.root = Path(output_dir) / mode; self.root.mkdir(parents=True, exist_ok=True)
        self.resume_dir = resume_dir; self.dataset_dir = dataset_dir
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.settings = dict(mode=mode, seeds=[535] if mode == "smoke" else [535, 536, 537],
            folds=2 if mode == "smoke" else 5, split_seed=535, inner_fraction=.15,
            epochs=1 if mode == "smoke" else 30, min_epochs=1 if mode == "smoke" else 3,
            patience=5, lr=1e-3, weight_decay=1e-2, dropout=.3, batch_size=64,
            embed_batch_size=16, max_len=35, bootstrap=50 if mode == "smoke" else 2000,
            encoders=ENCODERS, pipeline_version="1.0.0",
            code_sha256=COURSE_CODE_HASH if COURSE_CODE_HASH != "development" else file_sha(__file__))
        for name in ["config", "data_audit", "features", "logs", "runs", "tables", "figures", "presentation"]:
            (self.root / name).mkdir(exist_ok=True)
        self.logger = logging.getLogger(f"deepneoag.{id(self)}"); self.logger.setLevel(logging.INFO)
        self.logger.handlers.clear()
        self.logger.addHandler(logging.FileHandler(self.root / "logs/console.log", encoding="utf-8"))
        console = logging.StreamHandler(sys.stdout)
        console.addFilter(lambda record: not record.getMessage().startswith(("epoch ", "feature_batch ")))
        self.logger.addHandler(console)
        self.active = True; self.failed = False; self.registry = {}; self.selected = {}; self.features = {}
        self.figures = []; self.stage_times = []; self.plan_ids = set()
        torch.set_num_threads(min(4, os.cpu_count() or 1))
        plt.rcParams.update({"figure.figsize": (10, 5.5), "font.size": 11,
            "axes.spines.top": False, "axes.spines.right": False, "savefig.bbox": "tight"})
        self.status("initialized")

    def event(self, name, **kwargs):
        record = dict(time_utc=datetime.now(timezone.utc).isoformat(), event=name, **native(kwargs))
        with (self.root / "logs/events.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        self.logger.info("%s %s", name, json.dumps(native(kwargs)))

    def status(self, state, **extra):
        complete = list((self.root / "runs").glob("*/result.json"))
        atomic_json(self.root / "run_status.json", dict(status=state, mode=self.mode,
            warning="SMOKE — PIPELINE CHECK ONLY" if self.mode == "smoke" else None,
            completed_runs=len(complete), planned_runs=len(self.plan_ids),
            elapsed_seconds=time.monotonic() - self.started, **extra))

    def check_budget(self):
        if time.monotonic() - self.started >= self.budget:
            raise BudgetStop("Session budget reached; attach these outputs and set RESUME_DIR")

    def stage(self, name, fn):
        if not self.active: return
        started = time.monotonic(); self.event("stage_start", stage=name)
        try:
            fn(); self.event("stage_end", stage=name, seconds=time.monotonic() - started)
            self.stage_times.append(dict(stage=name, seconds=time.monotonic() - started))
            atomic_csv(self.root / "tables/stage_times.csv", pd.DataFrame(self.stage_times))
            if name != "completion": self.status("running", current_stage=name)
        except BudgetStop as e:
            self.active = False; self.status("partial", reason=str(e)); self.event("budget_stop", stage=name)
            self.export_archive()
        except Exception:
            self.active = False; self.failed = True
            detail = traceback.format_exc(); (self.root / "logs/error.txt").write_text(detail, encoding="utf-8")
            self.status("failed", stage=name, traceback=detail); self.export_archive(); raise

    def load_data(self):
        if self.mode == "full" and self.device.type != "cuda":
            raise RuntimeError("Full mode requires a GPU. Enable a Kaggle GPU accelerator.")
        self.data_path = find_dataset_directory(self.dataset_dir)
        self.event("dataset_resolved", path=str(self.data_path))
        train = pd.read_csv(self.data_path / "train.csv"); test = pd.read_csv(self.data_path / "test.csv")
        for name, frame, n, positives in [("train", train, 5608, 241), ("test", test, 1404, 61)]:
            assert len(frame) == n and frame.label.sum() == positives, f"Unexpected {name} counts"
            assert frame.label.isin([0, 1]).all() and frame.notna().all().all()
            assert frame.split.eq(name).all() and frame.id.is_unique
            assert frame.sequence.map(lambda s: bool(s) and set(s) <= set(AA) and len(s) <= 35).all()
            assert frame.length.eq(frame.sequence.str.len()).all()
        assert pd.concat([train, test]).sequence.is_unique, "Duplicate sequences"
        assert set(train.id).isdisjoint(test.id), "Overlapping IDs"
        checks = self.data_path / "checksums.sha256"
        checked = 0
        if checks.exists():
            for line in checks.read_text().splitlines():
                sha, relative = line.split("  ", 1)
                target = (self.data_path / relative).resolve()
                if not target.is_relative_to(self.data_path): raise ValueError("Unsafe manifest path")
                assert file_sha(target) == sha, f"Checksum mismatch: {relative}"
                checked += 1
        self.published_train = train.copy(); self.published_test = test.copy()
        self.data_hash = digest({"train": file_sha(self.data_path / "train.csv"),
                                 "test": file_sha(self.data_path / "test.csv")})
        if self.mode == "smoke":
            train = train_test_split(train, train_size=256, stratify=train.label, random_state=535)[0]
            test = train_test_split(test, train_size=64, stratify=test.label, random_state=535)[0]
        self.train = train.reset_index(drop=True); self.test = test.reset_index(drop=True)
        self.data_signature = digest(dict(data=self.data_hash, settings=self.settings,
            train_ids=self.train.id.tolist(), test_ids=self.test.id.tolist()))
        previous = self.root / "config/signature.json"
        if previous.exists() and json.loads(previous.read_text())["signature"] != self.data_signature:
            raise ValueError("Output directory belongs to a different experiment; use a fresh OUTPUT_DIR")
        if self.resume_dir:
            source = Path(self.resume_dir)
            if (source / self.mode / "config/signature.json").exists(): source /= self.mode
            prior = json.loads((source / "config/signature.json").read_text())
            if prior["signature"] != self.data_signature: raise ValueError("Resume signature mismatch")
            if source.resolve() != self.root.resolve():
                for group in ["features", "runs", "config", "tables", "data_audit"]:
                    shutil.copytree(source / group, self.root / group, dirs_exist_ok=True)
            self.event("resume_validated", source=str(source))
        atomic_json(previous, dict(signature=self.data_signature, dataset_hash=self.data_hash))
        atomic_json(self.root / "config/resolved_config.json", self.settings)
        versions = {}
        for package in ["torch", "numpy", "pandas", "scikit-learn", "fair-esm", "matplotlib"]:
            versions[package] = importlib.metadata.version(package)
        atomic_json(self.root / "config/environment.json", dict(packages=versions,
            python=sys.version, platform=platform.platform(), device=str(self.device),
            gpu=torch.cuda.get_device_name(0) if self.device.type == "cuda" else None,
            determinism="Seeded; deterministic algorithms requested with warn_only=True; inspect warnings."))
        atomic_csv(self.root / "data_audit/train_used.csv", self.train)
        atomic_csv(self.root / "data_audit/test_used.csv", self.test)
        atomic_json(self.root / "data_audit/audit.json", dict(published_train=len(self.published_train),
            published_test=len(self.published_test), used_train=len(self.train), used_test=len(self.test),
            train_positive=int(self.train.label.sum()), test_positive=int(self.test.label.sum()),
            exact_sequence_overlap=0, duplicates=0, checksum_files_verified=checked,
            length_35_ids=self.published_test.loc[self.published_test.length.eq(35), "id"].tolist(),
            similarity="Authors report 30% filtering; not independently recomputed."))
        self.folds = []; assignments = []
        splitter = StratifiedKFold(self.settings["folds"], shuffle=True, random_state=535)
        for fold, (outer_train, outer_val) in enumerate(splitter.split(self.train, self.train.label)):
            fit, stop = train_test_split(outer_train, test_size=.15, stratify=self.train.label.iloc[outer_train], random_state=535 + fold)
            assert not (set(fit) & set(stop) or set(fit) & set(outer_val) or set(stop) & set(outer_val))
            self.folds.append((fit, stop, outer_val, outer_train))
            for role, indices in [("fit", fit), ("early_stop", stop), ("outer_validation", outer_val)]:
                assignments.extend(dict(fold=fold, id=self.train.iloc[i].id, role=role, label=int(self.train.iloc[i].label)) for i in indices)
        atomic_csv(self.root / "data_audit/fold_assignments.csv", pd.DataFrame(assignments))
        self.event("data_validated", train=len(self.train), test=len(self.test), signature=self.data_signature)

    def figure(self, fig, name, caption):
        if self.mode == "smoke": fig.suptitle("SMOKE — PIPELINE CHECK ONLY", color="#a04a00", fontsize=12)
        fig.tight_layout()
        for ext in ["png", "svg"]: fig.savefig(self.root / "figures" / f"{name}.{ext}", dpi=300)
        plt.show(); plt.close(fig)
        self.figures.append(dict(id=name, file=f"figures/{name}.png", caption=caption, mode=self.mode))
        atomic_csv(self.root / "presentation/figure_index.csv", pd.DataFrame(self.figures))

    def explore(self):
        df = pd.concat([self.published_train, self.published_test])
        fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
        counts = pd.crosstab(df.split, df.label).reindex(["train", "test"])
        counts.columns = ["Other", "Neoantigen"]; counts.plot.bar(ax=axes[0], color=["#18354a", "#d78335"], rot=0)
        axes[0].set(title="Published class counts", ylabel="Peptides", xlabel="Split")
        for label, color in [(0, "#18354a"), (1, "#d78335")]:
            axes[1].hist(df.loc[df.label.eq(label), "length"], bins=np.arange(10.5, 36.5),
                histtype="step", linewidth=2, label=f"Label {label}", color=color)
        axes[1].set(title="Published peptide lengths", xlabel="Amino acids", ylabel="Peptides"); axes[1].legend()
        self.figure(fig, "V04_dataset", "Published counts and sequence lengths; no biological grouping inferred from length.")
        atomic_csv(self.root / "tables/dataset_counts.csv", counts.reset_index())
        atomic_csv(self.root / "tables/length_counts.csv", df.groupby(["split", "label", "length"]).size().rename("count").reset_index())

# SECTION: Frozen encoder extraction and immutable caches
class FeatureMixin:
    def prepare_features(self):
        self.features["composition"] = (composition_features(self.train.sequence), composition_features(self.test.sequence))
        self.features["onehot"] = (onehot_features(self.train.sequence), onehot_features(self.test.sequence))
        import esm
        combined = pd.concat([self.train, self.test], ignore_index=True)
        cache_rows = []
        for short, (name, layer, dim) in ENCODERS.items():
            self.check_budget(); started = time.monotonic()
            path = self.root / "features" / f"esm_{short}.npz"
            meta_path = path.with_suffix(".json")
            signature = digest(dict(project=self.data_signature, encoder=name, layer=layer, ids=combined.id.tolist()))
            if path.exists() and meta_path.exists():
                meta = json.loads(meta_path.read_text())
                if meta["signature"] != signature or meta["sha256"] != file_sha(path):
                    raise ValueError("Embedding cache signature/hash mismatch")
                with np.load(path) as cached:
                    assert cached["ids"].tolist() == combined.id.tolist()
                    assert np.array_equal(cached["lengths"], combined.length.values)
                    x = cached["embeddings"].astype(np.float32)
                self.event("feature_cache_hit", encoder=name)
            else:
                self.event("encoder_load", encoder=name)
                # FAIR checkpoints contain argparse.Namespace. Allowlist this exact
                # type for the official downloads instead of disabling safe loads globally.
                import argparse
                with torch.serialization.safe_globals([argparse.Namespace]):
                    model, alphabet = getattr(esm.pretrained, name)()
                model = model.to(self.device).eval()
                encoder_parameters = sum(p.numel() for p in model.parameters())
                for parameter in model.parameters(): parameter.requires_grad = False
                converter = alphabet.get_batch_converter()
                x = np.zeros((len(combined), 35, dim), dtype=np.float32)
                for start in range(0, len(combined), self.settings["embed_batch_size"]):
                    self.check_budget()
                    batch = combined.iloc[start:start + self.settings["embed_batch_size"]]
                    _, strings, tokens = converter(list(zip(batch.id, batch.sequence)))
                    with torch.no_grad():
                        reps = model(tokens.to(self.device), repr_layers=[layer], return_contacts=False)["representations"][layer]
                    for j, seq in enumerate(strings): x[start + j, :len(seq)] = reps[j, 1:len(seq) + 1].cpu().numpy()
                    if start % 256 == 0: self.event("feature_batch", encoder=name, completed=min(start + len(batch), len(combined)), total=len(combined))
                del model; torch.cuda.empty_cache()
                temp = path.with_suffix(".tmp.npz")
                np.savez_compressed(temp, embeddings=x.astype(np.float16), ids=combined.id.values.astype(str), lengths=combined.length.values)
                temp.replace(path)
                meta = dict(signature=signature, sha256=file_sha(path), encoder=name, layer=layer,
                    dim=dim, frozen=True, storage_dtype="float16", computation_dtype="float32",
                    extracted_seconds=time.monotonic() - started, records=len(combined), encoder_parameters=encoder_parameters)
                atomic_json(meta_path, meta)
                # All sessions train on the same stored values, including first extraction.
                x = x.astype(np.float16).astype(np.float32)
            assert x.shape == (len(combined), 35, dim) and np.isfinite(x).all()
            n = len(self.train); self.features[f"esm{short}"] = (x[:n], x[n:])
            pooled = masked_mean(x, combined.length.values).astype(np.float32)
            self.features[f"pool{short}"] = (pooled[:n], pooled[n:])
            cache_rows.append(dict(encoder=short, dim=dim, extraction_seconds=meta["extracted_seconds"],
                encoder_parameters=meta["encoder_parameters"],
                session_load_seconds=time.monotonic() - started, cache_bytes=path.stat().st_size))
        atomic_csv(self.root / "tables/encoder_costs.csv", pd.DataFrame(cache_rows))

# SECTION: Training, epoch checkpoints and resumption
class TrainingMixin:
    def build_model(self, c):
        dim = self.features[c["feature"]][0].shape[-1]
        return MaskedMCNN(dim, c["windows"], c["filters"], self.settings["dropout"]).to(self.device)

    def loader(self, x, lengths, y, indices, shuffle=False):
        ds = TensorDataset(torch.as_tensor(x[indices], dtype=torch.float32),
            torch.as_tensor(np.asarray(lengths)[indices], dtype=torch.long),
            torch.as_tensor(np.asarray(y)[indices], dtype=torch.float32))
        return DataLoader(ds, batch_size=self.settings["batch_size"], shuffle=shuffle, num_workers=0)

    def predict(self, model, x, lengths, indices=None):
        if indices is None: indices = np.arange(len(x))
        loader = self.loader(x, lengths, np.zeros(len(x)), indices)
        model.eval(); parts = []
        with torch.no_grad():
            for xx, ll, _ in loader:
                parts.append(torch.sigmoid(model(xx.to(self.device), ll.to(self.device))).cpu().numpy())
        return np.concatenate(parts)

    def train_neural(self, c, seed, fit, stop, run_dir, epochs, final=False):
        self.check_budget(); set_seed(seed)
        model = self.build_model(c); optimizer = torch.optim.AdamW(model.parameters(),
            lr=self.settings["lr"], weight_decay=self.settings["weight_decay"])
        x = self.features[c["feature"]][0]; y = self.train.label.values; lengths = self.train.length.values
        pw = float((y[fit] == 0).sum() / (y[fit] == 1).sum()) if c["weighted"] else 1.
        lossfn = nn.BCEWithLogitsLoss(pos_weight=torch.tensor(pw, device=self.device))
        train_loader = self.loader(x, lengths, y, fit, shuffle=True)
        latest = run_dir / "latest.pt"; best_path = run_dir / "best.pt"
        history = []; start_epoch = 0; best_ap = -1.; best_epoch = 0; stale = 0; training_seconds = 0.
        if latest.exists():
            saved = torch.load(latest, map_location=self.device, weights_only=False)
            if saved["config"] != c or saved["signature"] != self.data_signature: raise ValueError("Checkpoint mismatch")
            model.load_state_dict(saved["model"]); optimizer.load_state_dict(saved["optimizer"])
            start_epoch = saved["epoch"]; history = saved["history"]; best_ap = saved["best_ap"]
            best_epoch = saved["best_epoch"]; stale = saved["stale"]; training_seconds = saved["training_seconds"]
            random.setstate(saved["python_rng"]); np.random.set_state(saved["numpy_rng"])
            torch.set_rng_state(saved["torch_rng"].cpu())
            if self.device.type == "cuda" and saved["cuda_rng"] is not None:
                torch.cuda.set_rng_state_all([r.cpu() for r in saved["cuda_rng"]])
            self.event("epoch_resume", run=run_dir.name, next_epoch=start_epoch + 1)
        stopped = not final and start_epoch >= self.settings["min_epochs"] and stale >= self.settings["patience"]
        for ep in range(start_epoch, epochs) if not stopped else []:
            self.check_budget(); ep_started = time.monotonic(); model.train(); train_loss = 0.; count = 0
            for xx, ll, yy in train_loader:
                xx, ll, yy = xx.to(self.device), ll.to(self.device), yy.to(self.device)
                optimizer.zero_grad(set_to_none=True); loss = lossfn(model(xx, ll), yy)
                loss.backward(); optimizer.step(); train_loss += loss.item() * len(yy); count += len(yy)
            row = dict(epoch=ep + 1, train_loss=train_loss / count, lr=optimizer.param_groups[0]["lr"])
            improved = final
            if not final:
                prob = self.predict(model, x, lengths, stop)
                met = metrics(y[stop], prob); row.update({f"stop_{k}": v for k, v in met.items()})
                with torch.no_grad():
                    logits = torch.logit(torch.tensor(prob, device=self.device).clamp(1e-7, 1 - 1e-7))
                    row["stop_loss"] = float(lossfn(logits, torch.tensor(y[stop], dtype=torch.float32, device=self.device)).item())
                improved = met["ap"] > best_ap
                if improved: best_ap = float(met["ap"]); best_epoch = ep + 1; stale = 0
                else: stale += 1
            else: best_epoch = ep + 1
            row["epoch_seconds"] = time.monotonic() - ep_started
            training_seconds += row["epoch_seconds"]
            row["gpu_peak_memory_bytes"] = torch.cuda.max_memory_allocated() if self.device.type == "cuda" else 0
            history.append(row)
            if improved:
                tmp = best_path.with_suffix(".tmp"); torch.save(model.state_dict(), tmp); tmp.replace(best_path)
            saved = dict(model=model.state_dict(), optimizer=optimizer.state_dict(), epoch=ep + 1,
                config=c, signature=self.data_signature, history=history, best_ap=best_ap,
                best_epoch=best_epoch, stale=stale, training_seconds=training_seconds,
                python_rng=random.getstate(), numpy_rng=np.random.get_state(), torch_rng=torch.get_rng_state(),
                cuda_rng=torch.cuda.get_rng_state_all() if self.device.type == "cuda" else None)
            tmp = latest.with_suffix(".tmp"); torch.save(saved, tmp); tmp.replace(latest)
            atomic_csv(run_dir / "history.csv", pd.DataFrame(history))
            self.event("epoch", run=run_dir.name, **row)
            if not final and ep + 1 >= self.settings["min_epochs"] and stale >= self.settings["patience"]: break
        model.load_state_dict(torch.load(best_path, map_location=self.device, weights_only=True))
        return model, best_epoch, training_seconds, pw

    def execute_trial(self, c, fold, seed, final=False, epochs=None):
        cid = config_id(c); run_id = f"{cid}_{'final' if final else 'fold' + str(fold)}_seed{seed}"
        self.plan_ids.add(run_id); self.persist_plan()
        run_dir = self.root / "runs" / run_id; run_dir.mkdir(exist_ok=True)
        result_path = run_dir / "result.json"; prediction_path = run_dir / "predictions.csv"
        if result_path.exists():
            result = json.loads(result_path.read_text())
            if result["signature"] != self.data_signature or result["config"] != c: raise ValueError("Completed run mismatch")
            if result["predictions_sha256"] != file_sha(prediction_path): raise ValueError("Prediction checksum mismatch")
            return result, pd.read_csv(prediction_path)
        self.check_budget(); started = time.monotonic()
        atomic_json(run_dir / "config.json", dict(config=c, seed=seed, fold=fold, final=final, signature=self.data_signature))
        if final:
            fit = np.arange(len(self.train)); stop = None; outer = None
        else: fit, stop, outer, outer_train = self.folds[fold]
        xtr, xte = self.features[c["feature"]]
        if c["kind"] == "lr":
            # LR needs no early stopping and uses the complete outer-training portion.
            fit_lr = fit if final else outer_train
            model = make_pipeline(StandardScaler(), LogisticRegression(C=c["C"],
                class_weight="balanced", max_iter=2000, solver="lbfgs", random_state=535))
            model.fit(xtr[fit_lr], self.train.label.iloc[fit_lr])
            prob = model.predict_proba(xte if final else xtr[outer])[:, 1]
            parameters = int(model[-1].coef_.size + model[-1].intercept_.size)
            best_epoch = 0; seconds = time.monotonic() - started; pw = None
            with (run_dir / "model.pkl").open("wb") as f: pickle.dump(model, f)
        else:
            model, best_epoch, seconds, pw = self.train_neural(c, seed, fit, stop, run_dir,
                epochs or self.settings["epochs"], final)
            prob = self.predict(model, xte if final else xtr,
                self.test.length.values if final else self.train.length.values, None if final else outer)
            parameters = sum(p.numel() for p in model.parameters() if p.requires_grad)
            del model; torch.cuda.empty_cache()
        frame = (self.test if final else self.train.iloc[outer]).copy()
        frame["probability"] = prob; frame["config_id"] = cid; frame["seed"] = seed
        frame["fold"] = -1 if final else fold; frame["run_id"] = run_id
        atomic_csv(prediction_path, frame)
        result = dict(run_id=run_id, config_id=cid, config=c, signature=self.data_signature,
            fold=-1 if final else fold, seed=seed, final=final, best_epoch=best_epoch,
            trainable_parameters=parameters, training_seconds=seconds, pos_weight=pw,
            predictions_sha256=file_sha(prediction_path), **metrics(frame.label, prob))
        atomic_json(result_path, result); self.event("trial_complete", run=run_id, ap=result["ap"])
        self.status("running"); return result, frame

    def persist_plan(self):
        atomic_json(self.root / "config/planned_runs.json", sorted(self.plan_ids))

# SECTION: Controlled experiments and deterministic configuration selection
class ExperimentMixin:
    def evaluate_config(self, c):
        cid = config_id(c); self.registry[cid] = c
        seeds = [535] if c["kind"] == "lr" else self.settings["seeds"]
        results = []; predictions = []
        for fold in range(self.settings["folds"]):
            for seed in seeds: self.plan_ids.add(f"{cid}_fold{fold}_seed{seed}")
        self.persist_plan()
        for fold in range(self.settings["folds"]):
            for seed in seeds:
                result, frame = self.execute_trial(c, fold, seed)
                results.append(result); predictions.append(frame)
        result_frame = pd.DataFrame([{k: v for k, v in r.items() if k != "config"} for r in results])
        result_frame["family"] = c["family"]
        oof = pd.concat(predictions, ignore_index=True)
        assert oof.groupby("id").size().eq(len(seeds)).all() and oof.id.nunique() == len(self.train)
        ensemble = oof.groupby("id", sort=False).agg(label=("label", "first"),
            probability=("probability", "mean"), fold=("fold", "first")).reset_index()
        ensemble["config_id"] = cid
        atomic_csv(self.root / "tables" / f"{cid}_cv.csv", result_frame)
        atomic_csv(self.root / "tables" / f"{cid}_oof_raw.csv", oof)
        atomic_csv(self.root / "tables" / f"{cid}_oof.csv", ensemble)
        summary = dict(config_id=cid, family=c["family"], mean_ap=float(result_frame.ap.mean()),
            mean_mcc=float(result_frame.mcc.mean()), std_ap=float(result_frame.ap.std(ddof=1)),
            trainable_parameters=int(result_frame.trainable_parameters.iloc[0]),
            mean_training_seconds=float(result_frame.training_seconds.mean()),
            best_epochs=result_frame.best_epoch.tolist(), config=c)
        self.summaries[cid] = summary
        self.save_summaries(); return summary

    def save_summaries(self):
        rows = []
        for v in self.summaries.values():
            rows.append({k: val for k, val in v.items() if k not in ("config", "best_epochs")}
                | {"config_json": json.dumps(v["config"], sort_keys=True)})
        atomic_csv(self.root / "tables/cv_summary.csv", pd.DataFrame(rows))
        atomic_json(self.root / "config/experiment_registry.json", self.registry)

    def best(self, candidates):
        highest = max(s["mean_ap"] for s in candidates)
        tied = [s for s in candidates if highest - s["mean_ap"] <= 1e-6]
        return sorted(tied, key=lambda s: (-s["mean_mcc"], s["trainable_parameters"], s["config_id"]))[0]

    def experiments(self):
        self.summaries = {}
        smoke = self.mode == "smoke"; filters = 8 if smoke else 64
        windows = [2, 8] if smoke else [2, 3, 4, 5, 8]
        multi = [2, 3, 4, 5, 8]
        cs = [1.] if smoke else [.1, 1., 10.]
        def search(configs): return self.best([self.evaluate_config(c) for c in configs])
        self.selected["M0"] = search([lr_config("M0", "composition", c) for c in cs])
        self.selected["M1"] = search([neural_config("M1", "onehot", multi, filters)])
        self.selected["M2"] = search([lr_config("M2", "pool8M", c) for c in cs])
        self.selected["M3"] = search([neural_config("M3", "esm8M", [w], filters) for w in windows])
        filter_grid = [8, 16] if smoke else [32, 64, 128, 256]
        mc = [neural_config("M4", "esm8M", multi, f) for f in filter_grid]
        mc.append(neural_config("M4", "esm8M", multi, filters, False))
        self.selected["M4"] = search(mc)
        # Defaults are separately identified for matched-architecture comparisons.
        single_default = 2 if smoke else 3
        self.fixed_ids = dict(M0=config_id(lr_config("M0", "composition", 1)),
            M1=config_id(neural_config("M1", "onehot", multi, filters)),
            M2=config_id(lr_config("M2", "pool8M", 1)),
            M3=config_id(neural_config("M3", "esm8M", [single_default], filters)),
            M4=config_id(neural_config("M4", "esm8M", multi, filters)))
        self.selected["M5"] = search([lr_config("M5", "pool35M", c) for c in cs])
        single = self.selected["M3"]["config"]; multi_best = self.selected["M4"]["config"]
        self.selected["M6"] = search([neural_config("M6", "esm35M", single["windows"], single["filters"], single["weighted"])])
        self.selected["M7"] = search([neural_config("M7", "esm35M", multi_best["windows"], multi_best["filters"], multi_best["weighted"])])
        fixed = [{"comparison": "fixed_defaults", **{k: v for k, v in self.summaries[cid].items() if k not in ("config", "best_epochs")}} for cid in self.fixed_ids.values()]
        atomic_csv(self.root / "tables/fixed_configuration_comparison.csv", pd.DataFrame(fixed))
        atomic_json(self.root / "config/fixed_configurations.json", self.fixed_ids)

    def lock_selection(self):
        locks = {}
        for family, summary in self.selected.items():
            cid = summary["config_id"]; oof = pd.read_csv(self.root / "tables" / f"{cid}_oof.csv")
            threshold = choose_threshold(oof.label.values, oof.probability.values)
            epochs = int(math.ceil(np.median(summary["best_epochs"]))) if summary["config"]["kind"] == "cnn" else 0
            locks[family] = dict(config=summary["config"], config_id=cid,
                threshold=threshold, refit_epochs=epochs, selection_mean_ap=summary["mean_ap"],
                selection_note="CV used for tuning; not an unbiased post-selection estimate")
        self.locks = locks
        atomic_json(self.root / "config/locked_selection.json", dict(signature=self.data_signature, models=locks))
        atomic_csv(self.root / "tables/selected_models.csv", pd.DataFrame([
            dict(family=f, config_id=v["config_id"], threshold=v["threshold"], refit_epochs=v["refit_epochs"],
                 selection_mean_ap=v["selection_mean_ap"], config_json=json.dumps(v["config"])) for f, v in locks.items()]))
        self.event("selection_locked", models=list(locks))

# SECTION: Final refits, independent evaluation and uncertainty
class EvaluationMixin:
    def final_training(self):
        self.final_predictions = {}; self.final_results = []
        for family, lock in self.locks.items():
            c = lock["config"]; frames = []
            for seed in ([535] if c["kind"] == "lr" else self.settings["seeds"]):
                result, pred = self.execute_trial(c, -1, seed, final=True, epochs=lock["refit_epochs"])
                self.final_results.append(result); pred["family"] = family; frames.append(pred)
            raw = pd.concat(frames, ignore_index=True)
            self.final_predictions[family] = raw
            atomic_csv(self.root / "tables" / f"{family}_test_predictions_raw.csv", raw)

    def bootstrap_ci(self, y, prob, threshold):
        rng = np.random.default_rng(535); y = np.asarray(y); prob = np.asarray(prob)
        groups = [np.flatnonzero(y == label) for label in (0, 1)]; values = []
        for _ in range(self.settings["bootstrap"]):
            indices = np.concatenate([rng.choice(g, len(g), replace=True) for g in groups])
            met = metrics(y[indices], prob[indices], threshold)
            values.append([met["ap"], met["roc_auc"], met["mcc"]])
        array = np.asarray(values)
        return {k: {"lower": float(np.quantile(array[:, j], .025)),
                    "upper": float(np.quantile(array[:, j], .975))} for j, k in enumerate(["ap", "roc_auc", "mcc"])}

    def evaluate_test(self):
        rows = []; all_predictions = []; intervals = []
        for family, raw in self.final_predictions.items():
            lock = self.locks[family]
            ensemble = raw.groupby("id", sort=False).agg(label=("label", "first"),
                probability=("probability", "mean"), sequence=("sequence", "first"), length=("length", "first")).reset_index()
            assert set(ensemble.id) == set(self.test.id)
            ensemble["family"] = family; ensemble["config_id"] = lock["config_id"]
            ensemble["threshold"] = lock["threshold"]
            ensemble["prediction"] = (ensemble.probability >= lock["threshold"]).astype(int)
            ensemble["error_type"] = np.select([
                ensemble.label.eq(0) & ensemble.prediction.eq(1),
                ensemble.label.eq(1) & ensemble.prediction.eq(0)], ["FP", "FN"], default="correct")
            all_predictions.append(ensemble)
            for policy, threshold in [("fixed_0.5", .5), ("oof_selected", lock["threshold"])]:
                rows.append(dict(family=family, aggregation="ensemble", seed=-1, policy=policy,
                    config_id=lock["config_id"], **metrics(ensemble.label, ensemble.probability, threshold)))
                ci = self.bootstrap_ci(ensemble.label, ensemble.probability, threshold)
                intervals.extend(dict(family=family, policy=policy, metric=k, **bounds,
                    method="stratified percentile bootstrap", repetitions=self.settings["bootstrap"])
                    for k, bounds in ci.items())
                for seed, group in raw.groupby("seed"):
                    rows.append(dict(family=family, aggregation="single_seed", seed=int(seed), policy=policy,
                        config_id=lock["config_id"], **metrics(group.label, group.probability, threshold)))
        self.test_metrics = pd.DataFrame(rows); self.test_predictions = pd.concat(all_predictions, ignore_index=True)
        atomic_csv(self.root / "tables/test_metrics.csv", self.test_metrics)
        atomic_csv(self.root / "tables/test_predictions.csv", self.test_predictions)
        atomic_csv(self.root / "tables/test_confidence_intervals.csv", pd.DataFrame(intervals))
        errors = self.test_predictions.loc[self.test_predictions.error_type.ne("correct")].copy()
        errors["confidence_of_error"] = np.where(errors.error_type.eq("FP"), errors.probability, 1 - errors.probability)
        errors = errors.sort_values(["family", "error_type", "confidence_of_error"], ascending=[True, True, False])
        atomic_csv(self.root / "tables/error_analysis.csv", errors)
        atomic_csv(self.root / "presentation/error_examples.csv", errors.groupby(["family", "error_type"]).head(3))
        seed_metrics = self.test_metrics.query("aggregation == 'single_seed' and policy == 'oof_selected'")
        variability = seed_metrics.groupby("family")[["ap", "mcc", "recall", "precision"]].agg(["mean", "std"])
        variability.columns = [f"{metric}_{statistic}" for metric, statistic in variability.columns]
        atomic_csv(self.root / "tables/test_seed_variability.csv", variability.reset_index())

# SECTION: Evidence-based visualizations and presentation exports
class ReportingMixin:
    def make_plots(self):
        summary = pd.read_csv(self.root / "tables/cv_summary.csv")
        selected = pd.read_csv(self.root / "tables/selected_models.csv")
        cv = summary.set_index("config_id").loc[selected.config_id].reset_index()
        fig, ax = plt.subplots()
        ax.bar(cv.family, cv.mean_ap, yerr=cv.std_ap, color="#246d87", capsize=4)
        ax.set(ylim=(0, 1), ylabel="Average Precision", title="Selected configurations: CV mean and descriptive SD")
        self.figure(fig, "V11_cv_comparison", "Mean AP across outer folds/seeds; SD is descriptive, not a confidence interval; CV was used for selection.")
        # Full per-fold evidence, not just selected means.
        folds = pd.concat([pd.read_csv(self.root / "tables" / f"{cid}_cv.csv") for cid in selected.config_id])
        atomic_csv(self.root / "tables/selected_cv_runs.csv", folds)
        fig, ax = plt.subplots()
        for i, family in enumerate(sorted(folds.family.unique())):
            vals = folds.loc[folds.family.eq(family), "ap"].values
            offsets = np.linspace(-.16, .16, len(vals)); ax.scatter(i + offsets, vals, color="#246d87", s=24)
        ax.set(xticks=np.arange(8), xticklabels=sorted(folds.family.unique()), ylim=(0, 1),
            ylabel="Outer validation AP", title="Variation across fold and initialization")
        self.figure(fig, "V11_fold_seed", "Each point is one run; folds and initialization seeds are not independent samples.")
        histories = []
        for p in (self.root / "runs").glob("*/history.csv"):
            meta = json.loads((p.parent / "config.json").read_text())
            if not meta["final"]:
                h = pd.read_csv(p); h["run_id"] = p.parent.name
                h["family"] = meta["config"]["family"]; h["config_id"] = config_id(meta["config"])
                histories.append(h)
        history = pd.concat(histories, ignore_index=True)
        atomic_csv(self.root / "tables/all_epoch_history.csv", history)
        fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
        for family in ["M1", "M3", "M4", "M7"]:
            cid = self.locks[family]["config_id"]
            rows = history.loc[history.config_id.eq(cid)]
            first = rows.loc[rows.run_id.eq(rows.run_id.iloc[0])]
            axes[0].plot(first.epoch, first.train_loss, marker="o", label=family, color=FAMILY_COLORS[family])
            axes[1].plot(first.epoch, first.stop_ap, marker="o", label=family, color=FAMILY_COLORS[family])
        axes[0].set(title="Representative training histories", xlabel="Epoch", ylabel="Training loss (loss weights differ)")
        axes[1].set(title="Early-stopping subset", xlabel="Epoch", ylabel="Average Precision", ylim=(0, 1))
        axes[0].legend(); axes[1].legend()
        self.figure(fig, "V08_learning_curves", "First fold/seed for each selected configuration; loss scales with class weights, so compare AP rather than raw loss across losses.")
        # Controlled ablations: one factor changes within each panel.
        rows = []
        for cid, s in self.summaries.items():
            c = s["config"]
            if c["family"] in ("M3", "M4"):
                rows.append(dict(config_id=cid, family=c["family"], window=c["windows"][0] if len(c["windows"]) == 1 else "multi",
                    filters=c["filters"], weighted=c["weighted"], mean_ap=s["mean_ap"], std_ap=s["std_ap"],
                    parameters=s["trainable_parameters"], training_seconds=s["mean_training_seconds"]))
        ablations = pd.DataFrame(rows); atomic_csv(self.root / "tables/ablations.csv", ablations)
        fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))
        base_filters = 8 if self.mode == "smoke" else 64
        panels = [ablations.query("family == 'M3'"), ablations.query("family == 'M4' and weighted"),
                  ablations.query("family == 'M4' and filters == @base_filters")]
        for ax, frame, field, title in zip(axes, panels, ["window", "filters", "weighted"], ["Window size", "Filters per branch", "Class weighting"]):
            ax.bar(frame[field].astype(str), frame.mean_ap, yerr=frame.std_ap, capsize=3, color="#246d87")
            ax.set(title=title, ylabel="CV Average Precision", ylim=(0, 1))
        self.figure(fig, "V09_ablations", "One-factor ablations on ESM-2 8M. Error bars: descriptive SD across folds/seeds.")
        test = self.test_metrics.query("aggregation == 'ensemble' and policy == 'oof_selected'")
        atomic_csv(self.root / "presentation/final_comparison.csv", test)
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        for i, (family, frame) in enumerate(self.test_predictions.groupby("family")):
            precision, recall, _ = precision_recall_curve(frame.label, frame.probability)
            fpr, tpr, _ = roc_curve(frame.label, frame.probability)
            ap = average_precision_score(frame.label, frame.probability)
            style = "--" if family in ("M5", "M6", "M7") else "-"
            axes[0].step(recall, precision, where="post", label=f"{family}: AP={ap:.3f}", color=FAMILY_COLORS[family], linestyle=style)
            axes[1].plot(fpr, tpr, label=family, color=FAMILY_COLORS[family], linestyle=style)
        axes[0].axhline(self.test.label.mean(), color="grey", linestyle="--", label="Prevalence")
        axes[1].plot([0, 1], [0, 1], "--", color="grey")
        axes[0].set(title="Independent test precision–recall", xlabel="Recall", ylabel="Precision", xlim=(0, 1), ylim=(0, 1.02))
        axes[1].set(title="Independent test ROC", xlabel="False positive rate", ylabel="True positive rate", xlim=(0, 1), ylim=(0, 1.02))
        axes[0].legend(fontsize=8); axes[1].legend(fontsize=8)
        self.figure(fig, "V12_test_curves", "Frozen selections evaluated on held-out test; neural curves use mean probabilities across seeds.")
        fig, axes = plt.subplots(2, 4, figsize=(13, 6.5))
        for ax, (_, r) in zip(axes.flat, test.iterrows()):
            matrix = np.array([[r.tn, r.fp], [r.fn, r.tp]], dtype=int)
            ax.imshow(matrix, cmap="Blues")
            for (i, j), value in np.ndenumerate(matrix): ax.text(j, i, str(value), ha="center", va="center", color="black", bbox=dict(facecolor="white", alpha=.7, edgecolor="none"))
            ax.set(title=r.family, xticks=[0, 1], yticks=[0, 1], xlabel="Predicted", ylabel="True")
        self.figure(fig, "V12_confusion", "Raw counts at OOF-selected thresholds; class 1 is neoantigen.")
        costs = selected.merge(summary, on=["config_id", "family"], suffixes=("", "_cv"))
        fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
        for small, large in [("M2", "M5"), ("M3", "M6"), ("M4", "M7")]:
            subset = costs.set_index("family").loc[[small, large]]
            axes[0].plot(subset.index, subset.mean_ap, "o-", label=f"{small}/{large}", color=FAMILY_COLORS[small])
            axes[1].plot(subset.trainable_parameters, subset.mean_training_seconds, "o-", label=f"{small}/{large}", color=FAMILY_COLORS[small])
            for family, r in subset.iterrows(): axes[1].annotate(family, (r.trainable_parameters, r.mean_training_seconds))
        axes[0].set(title="8M vs 35M downstream CV", ylabel="Average Precision", ylim=(0, 1))
        axes[1].set(title="Downstream training cost", xlabel="Trainable downstream parameters", ylabel="Mean training seconds per fold/seed")
        axes[0].legend(); axes[1].legend()
        self.figure(fig, "V10_encoder_comparison", "8M/35M comparisons change embedding dimension and downstream parameter count. Frozen extraction costs are in encoder_costs.csv; timings are hardware-specific.")
        atomic_csv(self.root / "presentation/cv_comparison.csv", cv)
        summary_text = ["# Executed Evidence Summary", "", "SMOKE — PIPELINE CHECK ONLY. No scientific conclusions." if self.mode == "smoke" else "Independent test results follow configuration locking. No post-test tuning.", "",
            "CV selection scores are optimistic after tuning; fold/seed SD is descriptive, not a confidence interval.",
            "", "## Recorded results"]
        for _, row in test.iterrows():
            summary_text.append(f"- {row.family}: AP={row.ap:.4f}, MCC={row.mcc:.4f}, precision={row.precision:.4f}, recall={row.recall:.4f}; threshold={row.threshold:.4f}.")
        summary_text += ["", "## Interpretation boundaries", "- Composition vs one-hot changes both representation and classifier.",
            "- Mean-pooled ESM retains contextual sequence information.", "- Multiple windows also increase model capacity.",
            "- Other peptides are not guaranteed perfect biological negatives.", "- Exact duplicate checks do not validate the reported similarity threshold.",
            "- No HLA/MHC metadata is inferred from peptide length.", "- Predictions do not establish processing, presentation, T-cell response or clinical benefit."]
        (self.root / "presentation/executed_summary.md").write_text("\n".join(summary_text) + "\n", encoding="utf-8")

    def finish(self):
        if not self.active: return
        missing = [run for run in self.plan_ids if not (self.root / "runs" / run / "result.json").exists()]
        if missing: raise RuntimeError(f"Missing runs: {missing}")
        required = ["tables/test_metrics.csv", "tables/test_predictions.csv", "config/locked_selection.json", "presentation/figure_index.csv"]
        for path in required:
            if not (self.root / path).exists(): raise RuntimeError(f"Missing required artifact {path}")
        self.status("complete", models=8, expected_trials_verified=True)
        self.event("project_complete", models=8, runs=len(self.plan_ids))
        self.export_archive()

    def export_archive(self):
        target = self.root.parent / f"deepneoag_{self.mode}_results.zip"
        self.logger.info("Writing output archive: %s", target)
        for handler in self.logger.handlers: handler.flush()
        manifest = {str(p.relative_to(self.root)).replace("\\", "/"): file_sha(p)
            for p in self.root.rglob("*") if p.is_file() and p.name != "output_manifest.json" and not p.name.endswith(".tmp")}
        atomic_json(self.root / "output_manifest.json", manifest)
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as bundle:
            for p in self.root.rglob("*"):
                if p.is_file() and not p.name.endswith(".tmp"): bundle.write(p, str(Path(self.mode) / p.relative_to(self.root)))


class CourseProject(FeatureMixin, TrainingMixin, ExperimentMixin, EvaluationMixin, ReportingMixin, ProjectCore):
    pass
