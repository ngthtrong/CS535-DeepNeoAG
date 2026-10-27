"""Focused scientific and checkpoint acceptance checks; no encoder download."""
import ast
import json
import tempfile
import unittest
import zipfile
import types
from pathlib import Path

import nbformat
import numpy as np
import pandas as pd
import torch
from course_pipeline import (CourseProject, MaskedMCNN, masked_mean, metrics,
    choose_threshold, onehot_features, neural_config, set_seed, BudgetStop, file_sha,
    find_dataset_directory)

ROOT = Path(__file__).resolve().parents[1]


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="deepneoag_checks_")
        self.projects = []

    def tearDown(self):
        for p in self.projects:
            for handler in p.logger.handlers: handler.close()
            p.logger.handlers.clear()
        self.temp.cleanup()

    def project(self, suffix="a", resume=None):
        p = CourseProject("smoke", ROOT / "data", resume,
                          Path(self.temp.name) / suffix)
        self.projects.append(p); p.load_data(); return p

    def test_masked_mean_excludes_padding(self):
        x = np.array([[[2., 4.], [4., 8.], [900., 900.]]])
        np.testing.assert_allclose(masked_mean(x, [2]), [[3., 6.]])

    def csv_pair(self, relative):
        folder = Path(self.temp.name) / relative; folder.mkdir(parents=True, exist_ok=True)
        frame = pd.DataFrame([dict(id="a", sequence="ACDEFGHIKLM", label=0,
                                  split="train", length=11, source_file="a.fasta")])
        frame.to_csv(folder / "train.csv", index=False)
        frame.assign(split="test").to_csv(folder / "test.csv", index=False)
        return folder

    def test_dataset_parent_and_auto_discovery(self):
        folder = self.csv_pair("input/datasets/owner/cs535-deepneoag/extracted")
        root = Path(self.temp.name) / "input"
        self.assertEqual(find_dataset_directory(root / "datasets", root), folder.resolve())
        self.assertEqual(find_dataset_directory(None, root), folder.resolve())
        self.assertEqual(find_dataset_directory(folder, root), folder.resolve())

    def test_dataset_missing_path_reports_actual_inputs(self):
        folder = self.csv_pair("input/actual-slug")
        root = Path(self.temp.name) / "input"
        with self.assertRaisesRegex(ValueError, "DATASET_DIR does not exist") as error:
            find_dataset_directory(root / "CS535-DeepNeoAG", root)
        self.assertIn(str(folder / "train.csv"), str(error.exception))
        self.assertIn("DATASET_DIR=None", str(error.exception))

    def test_dataset_ambiguity_requires_explicit_selection(self):
        a = self.csv_pair("input/a"); self.csv_pair("input/b")
        root = Path(self.temp.name) / "input"
        with self.assertRaisesRegex(ValueError, "Found 2"):
            find_dataset_directory(None, root)
        self.assertEqual(find_dataset_directory(a, root), a.resolve())

    def test_dataset_checks_both_csv_schemas(self):
        folder = self.csv_pair("input/a")
        (folder / "test.csv").write_text("wrong_column\n1\n")
        with self.assertRaisesRegex(ValueError, "test.csv missing columns"):
            find_dataset_directory(folder, Path(self.temp.name) / "input")

    def test_cnn_padding_invariance_and_short_branch(self):
        set_seed(12); m = MaskedMCNN(3, [2, 3, 8], 4, 0).eval()
        x = torch.randn(2, 35, 3); lengths = torch.tensor([12, 5])
        changed = x.clone()
        for i, length in enumerate(lengths): changed[i, length:] = torch.randn_like(changed[i, length:]) * 1000
        with torch.no_grad():
            a, b = m(x, lengths), m(changed, lengths)
        self.assertTrue(torch.isfinite(a).all())
        torch.testing.assert_close(a, b, rtol=0, atol=0)

    def test_confusion_counts_and_ap(self):
        result = metrics([0, 0, 1, 1], [.1, .8, .4, .9])
        self.assertEqual([result[k] for k in ["tn", "fp", "fn", "tp"]], [1, 1, 1, 1])
        self.assertAlmostEqual(result["ap"], 5 / 6)

    def test_threshold_uses_mcc_and_tie_policy(self):
        y = np.array([0, 0, 1, 1]); p = np.array([.1, .2, .7, .8])
        self.assertEqual(choose_threshold(y, p), .5)
        threshold = choose_threshold(y, np.array([.8, .6, .7, .9]))
        candidates = [.0, .5, .6, .7, .8, .9, np.nextafter(.9, np.inf)]
        self.assertEqual(metrics(y, [.8, .6, .7, .9], threshold)["mcc"],
            max(metrics(y, [.8, .6, .7, .9], t)["mcc"] for t in candidates))

    def test_folds_and_no_test_members(self):
        p = self.project()
        self.assertEqual(len(p.train), 256); self.assertEqual(len(p.test), 64)
        observed = []
        for fit, stop, val, outer in p.folds:
            self.assertFalse(set(fit) & set(stop)); self.assertFalse(set(outer) & set(val))
            self.assertEqual(set(fit) | set(stop), set(outer))
            observed.extend(val)
            self.assertEqual(set(p.train.label.iloc[fit]), {0, 1})
            self.assertEqual(set(p.train.label.iloc[stop]), {0, 1})
        self.assertEqual(sorted(observed), list(range(256)))
        self.assertTrue(set(p.train.id).isdisjoint(p.published_test.id))

    def test_resume_signature_mismatch(self):
        p = self.project(); signature = p.root / "config/signature.json"
        saved = json.loads(signature.read_text()); saved["signature"] = "wrong"
        signature.write_text(json.dumps(saved))
        with self.assertRaisesRegex(ValueError, "Resume signature mismatch"):
            self.project("b", p.root)

    def test_interrupted_epoch_resume_matches_uninterrupted(self):
        p = self.project(); p.features["onehot"] = (onehot_features(p.train.sequence), onehot_features(p.test.sequence))
        c = neural_config("check", "onehot", [2, 3], 4)
        fit = np.arange(len(p.train)); stop = None
        baseline = p.root / "baseline"; baseline.mkdir()
        resumed = p.root / "resumed"; resumed.mkdir()
        expected, _, _, _ = p.train_neural(c, 535, fit, stop, baseline, 3, final=True)
        normal_budget = p.check_budget; calls = [0]
        def interrupt():
            calls[0] += 1
            if calls[0] == 3: raise BudgetStop("intentional acceptance-test interruption")
        p.check_budget = interrupt
        with self.assertRaises(BudgetStop): p.train_neural(c, 535, fit, stop, resumed, 3, final=True)
        self.assertEqual(torch.load(resumed / "latest.pt", weights_only=False)["epoch"], 1)
        p.check_budget = normal_budget
        actual, epoch, _, _ = p.train_neural(c, 535, fit, stop, resumed, 3, final=True)
        self.assertEqual(epoch, 3)
        for name, weight in expected.state_dict().items():
            torch.testing.assert_close(weight, actual.state_dict()[name], rtol=0, atol=0)

    def test_failed_stage_preserves_traceback(self):
        p = self.project()
        with self.assertRaisesRegex(RuntimeError, "intentional"):
            p.stage("intentional_failure", lambda: (_ for _ in ()).throw(RuntimeError("intentional")))
        self.assertEqual(json.loads((p.root / "run_status.json").read_text())["status"], "failed")
        self.assertIn("intentional", (p.root / "logs/error.txt").read_text())

    def test_partial_stage_does_not_continue(self):
        p = self.project()
        p.stage("budget", lambda: (_ for _ in ()).throw(BudgetStop("intentional")))
        p.stage("must_skip", lambda: self.fail("continued after budget stop"))
        self.assertEqual(json.loads((p.root / "run_status.json").read_text())["status"], "partial")

    def test_dataset_zip_and_notebook_standalone(self):
        with zipfile.ZipFile(ROOT / "dist/deepneoag-course-dataset.zip") as z:
            self.assertIsNone(z.testzip())
            self.assertEqual(sum(n.endswith(".fasta") for n in z.namelist()), 7012)
            self.assertFalse(any(n.endswith(".pdf") or n.endswith(".pt") for n in z.namelist()))
        nb = nbformat.read(ROOT / "notebooks/DeepNeoAG_Course_Project_Kaggle.ipynb", as_version=4)
        nbformat.validate(nb)
        for cell in nb.cells:
            if cell.cell_type == "code":
                ast.parse(cell.source)
                self.assertNotIn("from course_pipeline import", cell.source)

    def test_full_registry_contains_all_258_planned_fits(self):
        p = CourseProject("full", output_dir=Path(self.temp.name) / "registry")
        self.projects.append(p)
        def record_config(project, c):
            from course_pipeline import config_id
            cid = config_id(c); project.registry[cid] = c
            summary = dict(config_id=cid, family=c["family"], mean_ap=.2, mean_mcc=.1,
                std_ap=.01, trainable_parameters=100, mean_training_seconds=1.,
                best_epochs=[1], config=c)
            project.summaries[cid] = summary
            return summary
        p.evaluate_config = types.MethodType(record_config, p)
        p.experiments()
        lr = sum(c["kind"] == "lr" for c in p.registry.values())
        cnn = sum(c["kind"] == "cnn" for c in p.registry.values())
        self.assertEqual((lr, cnn), (9, 13))
        self.assertEqual(set(p.selected), {f"M{i}" for i in range(8)})
        self.assertEqual(lr * 5 + cnn * 5 * 3 + 3 + 5 * 3, 258)

    def test_completed_trial_is_reused_and_corruption_rejected(self):
        p = self.project()
        p.features["onehot"] = (onehot_features(p.train.sequence), onehot_features(p.test.sequence))
        c = neural_config("check", "onehot", [2], 4)
        result, frame = p.execute_trial(c, 0, 535)
        checkpoint = p.root / "runs" / result["run_id"] / "latest.pt"
        before = file_sha(checkpoint)
        again, same_frame = p.execute_trial(c, 0, 535)
        self.assertEqual(before, file_sha(checkpoint))
        self.assertEqual(result["run_id"], again["run_id"])
        self.assertEqual(frame.id.tolist(), same_frame.id.tolist())
        path = checkpoint.parent / "predictions.csv"
        path.write_text(path.read_text() + "\n")
        with self.assertRaisesRegex(ValueError, "checksum"):
            p.execute_trial(c, 0, 535)


if __name__ == "__main__":
    unittest.main(verbosity=2)
