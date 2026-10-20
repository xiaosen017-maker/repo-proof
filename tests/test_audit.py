import json
import sys
import unittest
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo_proof.audit import audit_manifest  # noqa: E402


class AuditTests(unittest.TestCase):
    def load(self, name: str):
        return json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))

    def test_healthy_manifest_is_accepted(self):
        report = audit_manifest(self.load("healthy.json"), now=datetime(2026, 10, 20, tzinfo=UTC))
        self.assertEqual(report.decision, "accept")
        self.assertEqual(report.critical_failures, ())
        self.assertEqual(report.score, report.max_score)

    def test_risky_manifest_is_rejected_with_explainable_failures(self):
        report = audit_manifest(self.load("risky.json"), now=datetime(2026, 10, 20, tzinfo=UTC))
        self.assertEqual(report.decision, "reject")
        self.assertIn("snapshot.full_sha", report.critical_failures)
        self.assertIn("repo.license", report.critical_failures)
        self.assertIn("milestone.linked_work", report.critical_failures)

    def test_invalid_schema_is_rejected_before_scoring(self):
        manifest = self.load("healthy.json")
        manifest["schema_version"] = 99
        with self.assertRaisesRegex(ValueError, "schema_version"):
            audit_manifest(manifest)


if __name__ == "__main__":
    unittest.main()
