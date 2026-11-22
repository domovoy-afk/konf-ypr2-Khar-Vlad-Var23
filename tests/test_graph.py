"""Проверки синтаксиса тестового источника и обхода графа."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from graph import dependency_graph, read_test_graph

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "graph.txt"


class GraphTest(unittest.TestCase):
    """Использует тестовый репозиторий из примеров."""

    def setUp(self):
        self.packages = read_test_graph(EXAMPLE)

    def test_breadth_first_and_shared_dependency(self):
        graph, depths = dependency_graph(self.packages, "A", 3, "")
        self.assertEqual(list(graph), ["A", "B", "C", "D", "E"])
        self.assertEqual(depths, {"A": 0, "B": 1, "C": 1, "D": 2, "E": 3})
        self.assertEqual(graph["B"], ["D"])
        self.assertEqual(graph["C"], ["D"])

    def test_depth_limit(self):
        graph, depths = dependency_graph(self.packages, "A", 1, "")
        self.assertEqual(graph, {"A": ["B", "C"], "B": [], "C": []})
        self.assertEqual(depths, {"A": 0, "B": 1, "C": 1})
        graph, _ = dependency_graph(self.packages, "A", 0, "")
        self.assertEqual(graph, {"A": []})

    def test_filter(self):
        graph, _ = dependency_graph(self.packages, "A", 3, "D")
        self.assertEqual(graph, {"A": ["B", "C"], "B": [], "C": []})

    def test_cycle(self):
        graph, depths = dependency_graph(self.packages, "F", 9, "")
        self.assertEqual(graph, {"F": ["G"], "G": ["F"]})
        self.assertEqual(depths, {"F": 0, "G": 1})

    def test_unknown_root(self):
        with self.assertRaisesRegex(ValueError, "Z"):
            dependency_graph(self.packages, "Z", 3, "")

    def test_malformed_input(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "invalid.txt"
            for line in ("A B", "A: b", "A: B\nA: C"):
                with self.subTest(line=line):
                    path.write_text(line, encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "invalid.txt"):
                        read_test_graph(path)
