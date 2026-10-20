import csv
import tempfile
import unittest
from pathlib import Path

from practice_classroom.case1_waste_heat.monte_carlo_case1 import run_monte_carlo


class MonteCarloCase1Tests(unittest.TestCase):
    def test_sampling_is_reproducible_and_writes_each_iteration(self):
        repo_root = Path(__file__).resolve().parents[1]
        config_path = (
            repo_root
            / "practice_classroom"
            / "case1_waste_heat"
            / "student_template.yaml"
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "samples.csv"
            samples = run_monte_carlo(
                config_path, output_path, iterations=25, seed=1234
            )
            repeated = run_monte_carlo(
                config_path,
                Path(temp_dir) / "repeated.csv",
                iterations=25,
                seed=1234,
            )

            self.assertEqual(samples, repeated)
            self.assertEqual(len(samples), 25)
            self.assertEqual(
                len({row["cost_savings_usd_per_ref"] for row in samples}), 25
            )
            with output_path.open(newline="", encoding="utf-8") as csv_file:
                self.assertEqual(len(list(csv.DictReader(csv_file))), 25)

    def test_rejects_zero_iterations(self):
        repo_root = Path(__file__).resolve().parents[1]
        config_path = (
            repo_root
            / "practice_classroom"
            / "case1_waste_heat"
            / "student_template.yaml"
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaisesRegex(ValueError, "at least 1"):
                run_monte_carlo(
                    config_path, Path(temp_dir) / "samples.csv", iterations=0
                )


if __name__ == "__main__":
    unittest.main()
