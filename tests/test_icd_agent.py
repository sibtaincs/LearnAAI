import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from learnaai.icd_agent import ICDAgent


class TestICDAgent(unittest.TestCase):
    def test_search_code_returns_cholera_rows(self):
        db_path = Path(__file__).resolve().parents[1] / "UpdatedLangchain" / "icd10cm_real.db"
        agent = ICDAgent(db_path=db_path)

        rows = agent.search_code("cholera", limit=3)

        self.assertGreater(len(rows), 0)
        self.assertTrue(any(code.startswith("A00") for code, _ in rows))


if __name__ == "__main__":
    unittest.main()
