from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

import pandas as pd


EXERCISE_DIR = Path(__file__).resolve().parents[1] / "Exercises" / "Experiment Analysis"


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, EXERCISE_DIR / filename)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {filename}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ANALYSIS = load_module("experiment_analysis", "experiment_analysis.py")
GENERATOR = load_module("experiment_data_generator", "generate_example_data.py")


class ExperimentAnalysisTests(unittest.TestCase):
    def test_reports_lift_and_counts(self) -> None:
        data = pd.DataFrame(
            [
                ["c1", "control", 0],
                ["c2", "control", 1],
                ["c3", "control", 0],
                ["t1", "treatment", 1],
                ["t2", "treatment", 1],
                ["t3", "treatment", 0],
            ],
            columns=["user_id", "variant", "converted"],
        )

        result = ANALYSIS.analyze_experiment(data)

        self.assertEqual(result["control"]["users"], 3)
        self.assertEqual(result["treatment"]["conversions"], 2)
        self.assertAlmostEqual(result["absolute_lift"], 1 / 3)
        self.assertEqual(len(result["confidence_interval_95"]), 2)
        self.assertGreaterEqual(result["p_value_two_sided"], 0)
        self.assertLessEqual(result["p_value_two_sided"], 1)

    def test_rejects_duplicate_users_and_non_binary_outcomes(self) -> None:
        duplicate = pd.DataFrame(
            [["same", "control", 0], ["same", "treatment", 1]],
            columns=["user_id", "variant", "converted"],
        )
        with self.assertRaisesRegex(ValueError, "user_id values must be unique"):
            ANALYSIS.analyze_experiment(duplicate)

        invalid = pd.DataFrame(
            [["c1", "control", 0], ["t1", "treatment", 2]],
            columns=["user_id", "variant", "converted"],
        )
        with self.assertRaisesRegex(ValueError, "binary values"):
            ANALYSIS.analyze_experiment(invalid)

    def test_generator_is_byte_for_byte_reproducible(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.csv"
            second = Path(directory) / "second.csv"
            GENERATOR.generate_example_data(first, seed=41, users_per_variant=20)
            GENERATOR.generate_example_data(second, seed=41, users_per_variant=20)

            self.assertEqual(first.read_bytes(), second.read_bytes())


if __name__ == "__main__":
    unittest.main()
