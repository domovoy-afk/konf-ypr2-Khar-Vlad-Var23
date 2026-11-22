"""Проверки представления графа в формате D2."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from d2_graph import format_d2


class D2GraphTest(unittest.TestCase):
    """Проверяет отдельные узлы, спецсимволы и циклические ребра."""

    def test_package_labels_and_cycle(self):
        graph = {"libstdc++6": ["g++-14"], "g++-14": ["libstdc++6"]}
        result = format_d2(graph)
        self.assertIn('p0: "libstdc++6"', result)
        self.assertIn('p1: "g++-14"', result)
        self.assertIn("p0 -> p1\np1 -> p0", result)

    def test_isolated_node(self):
        result = format_d2({"H": []})
        self.assertIn('p0: "H"', result)
        self.assertNotIn("->", result)
