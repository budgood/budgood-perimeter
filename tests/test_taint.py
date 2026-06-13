import unittest
from budgood_perimeter import taint


class TestTaint(unittest.TestCase):
    def test_grade_extracted(self):
        rec = {"text": "x", "tier": "T5", "confidence": "low", "irrelevant": 1}
        self.assertEqual(taint.grade_of(rec), {"tier": "T5", "confidence": "low"})

    def test_attach(self):
        lab = taint.attach("hit", {"tier": "T0"})
        self.assertEqual(lab.value, "hit")
        self.assertEqual(lab.grade, {"tier": "T0"})

    def test_preserve_wraps_leaking_reader(self):
        def leaking():                      # returns (value, source_record) pairs
            return [("alpha", {"tier": "T5", "confidence": "low"}),
                    ("beta", {"tier": "T0"})]
        out = taint.preserve(leaking)()
        self.assertEqual(out[0].value, "alpha")
        self.assertEqual(out[0].grade, {"tier": "T5", "confidence": "low"})
        self.assertEqual(out[1].grade, {"tier": "T0"})


if __name__ == "__main__":
    unittest.main()
