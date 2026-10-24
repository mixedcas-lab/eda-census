"""Offline tests: python3 -m unittest discover -s collector -v"""
import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # noqa: E402
import classify as C  # noqa: E402


class TestRelevance(unittest.TestCase):
    def test_core(self):
        for t in ("GRID: A Graph RL and gm/ID-Based Framework for Fast and Transferable Analog Circuit Optimization",
                  "A Reusable Code-Based SAR ADC Design With CDAC Compiler and Synthesizable Analog Building Blocks",
                  "A 0.0043-mm2 0.3–1.2-V Frequency-Scalable Synthesized Fractional-N Digital PLL",
                  "An Automated SerDes Frontend Generator Verified With a 16-nm Instance Achieving 15 Gb/s at 1.96 pJ/bit",
                  "ALAG: A Silicon-Proven, Non-Fixed-Grid Framework for Hierarchical Analog Layout Automation",
                  "Elitist nondominated sorting genetic algorithm based RF IC optimizer for amplifier design",
                  "A 0.0067-mm2 12-bit 20-MS/s SAR ADC Using Digital Place-and-Route Tools in 40-nm CMOS"):
            self.assertEqual(C.relevance(t, ""), "core", t)

    def test_circuits_and_digital_eda_are_out(self):
        for t in ("A fully integrated CMOS frequency synthesizer with charge-averaging charge pump",
                  "A high precision ramp generator for low cost ADC test",
                  "CAUTS: Clock Tree Optimization via Skewed Cells With Complementary Asymmetrical Uniform Transistor Sizing",
                  "Automatic and continuous offset compensation of MOS operational amplifiers using floating-gate transistors",
                  "An Envelope Tracking Supply Modulator With Average Power Tracking-Based Switch Sizing",
                  "A Foreground Calibration for Time-Interleaved Analog-to-Digital Converters Based on Genetic Algorithm",
                  "Reliability-Oriented Placement and Routing Algorithm for SRAM-Based FPGAs"):
            self.assertIsNone(C.relevance(t, ""), t)


class TestTags(unittest.TestCase):
    def test_tags(self):
        t = "GRID: A Graph RL and gm/ID-Based Framework for Fast and Transferable Analog Circuit Optimization"
        self.assertEqual(C.da_type(t, ""), "ML-based")
        self.assertIn("Sizing/optimization", C.architectures(t, ""))
        self.assertEqual(set(C.modulations(t, "")) >= {"Reinforcement learning", "Graph neural network", "gm/ID / knowledge-based"}, True)
        self.assertIn("ADC/DAC", C.applications("A SAR ADC compiler", ""))

    def test_speedup(self):
        self.assertEqual(C.parse_specs("x", "The framework achieves a 9.4× speedup over Bayesian optimization.")["speedup"], 9.4)
        self.assertEqual(C.parse_specs("x", "It needs 5x fewer simulations.")["speedup"], 5.0)
        self.assertNotIn("speedup", C.parse_specs("x", "It is 3× faster than BO and 10× faster than RL."))


class TestBuild(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.cache = os.path.join(self.tmp, "cache")
        os.makedirs(self.cache)
        self._papers, self._meta = build.PAPERS, build.META
        build.PAPERS = os.path.join(self.tmp, "papers.json")
        build.META = os.path.join(self.tmp, "meta.json")

    def tearDown(self):
        build.PAPERS, build.META = self._papers, self._meta
        shutil.rmtree(self.tmp)

    def put(self, n, title, pub, abstract="", year=2025):
        with open(os.path.join(self.cache, "%d.json" % n), "w", encoding="utf-8") as f:
            json.dump({"article_number": n, "title": title, "publication_title": pub, "abstract": abstract,
                       "publication_year": year, "publication_date": "Feb. %d" % year, "doi": "10.1109/x.%d" % n,
                       "authors": {"authors": [{"full_name": "A. Kim", "author_order": 1,
                                                "affiliation": "KAIST, Daejeon, South Korea"}]}}, f)

    def test_rebuild(self):
        config = build.load_json(build.CONFIG, None)
        self.put(1, "Reinforcement Learning for Analog Circuit Sizing", "2025 62nd ACM/IEEE Design Automation Conference (DAC)",
                 "It is 12× faster than the baseline.")
        self.put(2, "A 12-b SAR ADC", "IEEE Journal of Solid-State Circuits")
        self.put(3, "Analog Layout Automation With Graph Neural Networks",
                 "2025 30th Asia and South Pacific Design Automation Conference (ASP-DAC)")
        meta = build.rebuild(config, self.cache, "2026-10-24")
        papers = {p["id"]: p for p in build.load_json(build.PAPERS, [])}
        self.assertEqual(set(papers), {"1", "3"})
        self.assertEqual((papers["1"]["v"], papers["1"]["ty"], papers["1"]["s"]["speedup"]), ("DAC", "ML-based", 12.0))
        self.assertEqual(papers["3"]["v"], "ASP-DAC")
        self.assertNotIn("abstract", json.dumps(list(papers.values())))
        self.assertEqual(meta["core"], 2)


if __name__ == "__main__":
    unittest.main()
