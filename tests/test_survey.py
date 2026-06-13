import json
import unittest
import tempfile
import shutil
from pathlib import Path
from budgood_perimeter import config as C, survey as V, staleness as St

FX = Path(__file__).resolve().parent / "fixtures"


class TestSurvey(unittest.TestCase):
    def setUp(self):
        # copy fixtures to a temp dir so attest() writes don't dirty the repo
        self.tmp = Path(tempfile.mkdtemp())
        shutil.copytree(FX, self.tmp / "fx")
        self.cfg = C.load(self.tmp / "fx" / "perimeter.toml")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_scan_born_died_changed(self):
        d = V.scan(self.cfg)
        self.assertEqual(d["born"], ["reader_b.py"])     # unregistered reader appears
        self.assertEqual(d["died"], [])
        self.assertEqual(d["changed"], [])
        self.assertEqual(d["predicate_version"], "v1")

    def test_attest_thin_detection(self):
        # has a real diff (reader_b born) -> not thin even with empty review
        rec = V.attest(self.cfg, by="test")
        self.assertFalse(rec["thin"])
        self.assertIn("reader_b.py", rec["channel_diff"]["born"])

    def test_manual_channel_not_died(self):
        # a manual (predicate-blind) channel must NOT be reported as died
        with self.cfg.manifest_path.open("a", encoding="utf-8") as f:
            f.write('{"id":"CH-M","type":"channel","status":"active","path":"ghost.py","found_under_predicate":"manual"}\n')
        self.assertNotIn("ghost.py", V.scan(self.cfg)["died"])

    def test_status_never_complete(self):
        s = V.status(self.cfg)
        self.assertIn("owned", s)
        self.assertNotIn("complete", json.dumps(s))

    def test_staleness_never_surveyed(self):
        msg = St.check(self.cfg)   # attestations.jsonl empty
        self.assertIsNotNone(msg)
        self.assertIn("never been surveyed", msg)


if __name__ == "__main__":
    unittest.main()


class TestLabels(unittest.TestCase):
    def setUp(self):
        self.cfg = __import__("budgood_perimeter.config", fromlist=["load"]).load(
            __import__("pathlib").Path(__file__).resolve().parent / "fixtures" / "perimeter.toml")

    def test_leak_listed(self):
        from budgood_perimeter import survey as V
        r = V.label_report(self.cfg)
        leak_paths = {c["path"] for c in r["leak"]}
        preserve_paths = {c["path"] for c in r["preserving"]}
        self.assertIn("reader_c.py", leak_paths)       # false -> leak
        self.assertIn("reader_a.py", preserve_paths)   # true -> preserving
