import tempfile
import unittest
from pathlib import Path
from retirelab import RetirementScenario, analyze, project
from retirelab.storage import ScenarioStore

class EngineTests(unittest.TestCase):
    def test_reject_ages(self):
        with self.assertRaises(ValueError):
            RetirementScenario(current_age=70, retirement_age=65)

    def test_reject_negative_savings(self):
        with self.assertRaises(ValueError):
            RetirementScenario(current_savings=-1)

    def test_zero_return_math(self):
        s = RetirementScenario(current_age=30, retirement_age=32, end_age=33,
            current_savings=100, annual_contribution=50, annual_spending=0,
            expected_return=0, contribution_growth=0)
        self.assertEqual(project(s).retirement_balance, 200)

    def test_funding_shortfall(self):
        s = RetirementScenario(current_age=30, retirement_age=30, end_age=32,
            current_savings=100, annual_spending=80, annual_other_income=0,
            expected_return=0, inflation_rate=0)
        self.assertEqual(project(s).total_shortfall, 60)

    def test_reproducibility(self):
        s = RetirementScenario()
        self.assertEqual(analyze(s, 20, 7), analyze(s, 20, 7))

    def test_persistence(self):
        with tempfile.TemporaryDirectory() as temp:
            store = ScenarioStore(Path(temp) / "scenarios.db")
            scenario = RetirementScenario()
            identifier = store.save(scenario)
            self.assertEqual(store.get(identifier), scenario)
            self.assertTrue(store.delete(identifier))
            self.assertIsNone(store.get(identifier))

if __name__ == "__main__":
    unittest.main()
