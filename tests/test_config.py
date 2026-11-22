"""Проверки YAML и каждого обязательного параметра."""

import sys
import tempfile
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from config import load_config


class ConfigTest(unittest.TestCase):
    """Загружает временный YAML с разными наборами параметров."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.path = Path(temporary.name) / "config.yaml"
        self.data = {
            "package": "hello",
            "repository": "https://archive.ubuntu.com/ubuntu/",
            "test_mode": False,
            "max_depth": 0,
            "exclude_substring": "",
        }

    def load(self, **overrides):
        """Сохраняет конфигурацию и читает ее через публичную функцию."""
        source = yaml.safe_dump(self.data | overrides)
        self.path.write_text(source, encoding="utf-8")
        return load_config(self.path)

    def test_valid_configs(self):
        self.assertEqual(self.load().package, "hello")
        graph = self.path.with_name("graph.txt")
        graph.touch()
        config = self.load(package="AA", repository=graph.name, test_mode=True)
        self.assertEqual(Path(config.repository), graph)

    def test_invalid_values(self):
        cases = [
            ("package", "a b"),
            ("repository", "archive.ubuntu.com"),
            ("repository", "https://"),
            ("repository", "https://example.com:invalid"),
            ("test_mode", "true"),
            ("max_depth", -1),
            ("max_depth", True),
            ("exclude_substring", None),
        ]
        for name, value in cases:
            with self.subTest(name=name, value=value):
                with self.assertRaisesRegex(ValueError, name):
                    self.load(**{name: value})

    def test_missing_test_graph(self):
        with self.assertRaisesRegex(ValueError, "repository"):
            self.load(package="A", repository="missing.txt", test_mode=True)

    def test_missing_key(self):
        del self.data["package"]
        with self.assertRaisesRegex(ValueError, "package"):
            self.load()

    def test_unknown_key(self):
        with self.assertRaisesRegex(ValueError, "typo"):
            self.load(typo=True)

    def test_broken_yaml(self):
        self.path.write_text("package: [", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "YAML"):
            load_config(self.path)
