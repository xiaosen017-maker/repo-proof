import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo_proof.cli import main  # noqa: E402


class CliTests(unittest.TestCase):
    def test_markdown_report_is_written(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "report.md"
            code = main(["audit", str(ROOT / "examples" / "healthy.json"), "--output", str(output)])
            self.assertEqual(code, 0)
            text = output.read_text(encoding="utf-8")
            self.assertIn("Decision: **ACCEPT**", text)
            self.assertIn("snapshot.full_sha", text)

    def test_json_report_returns_two_for_rejection(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "report.json"
            code = main([
                "audit", str(ROOT / "examples" / "risky.json"),
                "--format", "json", "--output", str(output),
            ])
            self.assertEqual(code, 2)
            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(data["decision"], "reject")


if __name__ == "__main__":
    unittest.main()
