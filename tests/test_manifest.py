import unittest
from pathlib import Path
from budgood_perimeter import config as C, manifest as M

FX = Path(__file__).resolve().parent / "fixtures"


class TestManifest(unittest.TestCase):
    def setUp(self):
        self.cfg = C.load(FX / "perimeter.toml")

    def test_active_predicate(self):
        bt = M.load(self.cfg.manifest_path)
        pred = M.active_predicate(bt)
        self.assertIsNotNone(pred)
        self.assertEqual(pred["version"], "v1")

    def test_registered_paths(self):
        bt = M.load(self.cfg.manifest_path)
        self.assertEqual(M.registered_channel_paths(bt), {"reader_a.py", "reader_c.py"})

    def test_latest_by_id_active(self):
        bt = M.load(self.cfg.manifest_path)
        self.assertEqual(len(bt.get("unowned", [])), 1)


if __name__ == "__main__":
    unittest.main()
