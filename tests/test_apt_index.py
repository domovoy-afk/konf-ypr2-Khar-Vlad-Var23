"""Проверки чтения индексов и разбора отношений пакетов."""

import gzip
import io
import lzma
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from apt_index import fetch_index, index_url, parse_index


INDEX = (
    "Package: example\n"
    "Depends: libc6 (>= 2.38), libfoo:any |\n"
    " libbar (= 1:2.3-1), libc6\n"
    "Pre-Depends: dpkg\n"
    "Description: Example\n"
    " Depends: ignored continuation\n"
    "Recommends: recommend-me\n\n"
    "Package: libfoo\n"
)


class AptIndexTest(unittest.TestCase):
    """Проверяет метаданные, кодировки индекса и граничные случаи."""

    def test_parse_index(self):
        packages = parse_index(io.StringIO(INDEX))
        self.assertEqual(
            packages,
            {"example": ("dpkg", "libc6", "libfoo", "libbar"), "libfoo": ()},
        )

    def test_empty_index(self):
        with self.assertRaisesRegex(ValueError, "Packages"):
            parse_index(io.StringIO(""))

    def test_index_url(self):
        base = "https://archive.ubuntu.com/ubuntu/"
        self.assertEqual(
            index_url(base), base + "dists/noble/main/binary-amd64/Packages.xz"
        )
        direct = "https://example.org/Packages.gz?token=example"
        self.assertEqual(index_url(direct), direct)

    def test_fetch_index_formats(self):
        data = INDEX.encode()
        archives = {
            "Packages": data,
            "Packages.gz": gzip.compress(data),
            "Packages.xz": lzma.compress(data),
        }
        for name, archive in archives.items():
            with self.subTest(name=name):
                with patch("apt_index.urlopen", return_value=io.BytesIO(archive)):
                    result = fetch_index(f"https://example.org/{name}")
                self.assertIn("example", result)
