"""Fixture walker — every detector must have a fixture dir, every fixture must pass.

A fixture is tests/fixtures/<detector>/<case>.json:

    {
      "input": "...",                      # the opaque string
      "expect_type": "jwt",                # top-ranked candidate type
      "summary_contains": ["JWT"],         # optional fragments of top summary
      "details": {"alg": "HS256"}          # optional exact top-level detail values
    }
"""

import json
import pathlib
import unittest

import dring

FIX = pathlib.Path(__file__).parent / "fixtures"


class TestDetectorCoverage(unittest.TestCase):
    def test_every_detector_has_a_fixture_and_vice_versa(self):
        names = {m.NAME for m in dring.DETECTORS}
        dirs = {p.name for p in FIX.iterdir() if p.is_dir()}
        self.assertEqual(
            names, dirs,
            "each detector needs a fixture dir with the same name (and no orphan dirs)",
        )


class TestFixtures(unittest.TestCase):
    pass


def _make(case):
    def test(self):
        spec = json.loads(case.read_text())
        cands = dring.identify(spec["input"])
        self.assertTrue(cands, f"no candidates for {case}")
        top = cands[0]
        self.assertEqual(top["type"], spec["expect_type"],
                         f"top candidate was {top['type']}: {top['summary']}")
        for frag in spec.get("summary_contains", []):
            self.assertIn(frag, top["summary"])
        for k, v in spec.get("details", {}).items():
            self.assertEqual(top["details"].get(k), v)

    return test


for _case in sorted(FIX.glob("*/*.json")):
    setattr(TestFixtures, f"test_{_case.parent.name}_{_case.stem}", _make(_case))


if __name__ == "__main__":
    unittest.main()
