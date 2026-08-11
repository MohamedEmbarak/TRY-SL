import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bigfiles import human, largest, main  # noqa: E402


class Sizes(unittest.TestCase):
    def test_bytes_below_1k(self):
        self.assertEqual(human(512), "512B")

    def test_scales_to_kb(self):
        self.assertEqual(human(2048), "2.0KB")

    def test_scales_to_mb(self):
        self.assertEqual(human(5 * 1024 * 1024), "5.0MB")


class Largest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        for name, size in (("a", 300), ("b", 100), ("c", 200)):
            with open(os.path.join(self.tmp.name, name), "wb") as fh:
                fh.write(b"x" * size)

    def test_orders_by_size_descending(self):
        rows = largest(self.tmp.name, 3)
        self.assertEqual([os.path.basename(p) for _s, p in rows], ["a", "c", "b"])

    def test_count_limits_results(self):
        self.assertEqual(len(largest(self.tmp.name, 2)), 2)

    def test_recurses_into_subdirectories(self):
        sub = os.path.join(self.tmp.name, "sub")
        os.mkdir(sub)
        with open(os.path.join(sub, "big"), "wb") as fh:
            fh.write(b"x" * 999)
        self.assertEqual(os.path.basename(largest(self.tmp.name, 1)[0][1]), "big")

    def test_empty_directory_yields_nothing(self):
        with tempfile.TemporaryDirectory() as empty:
            self.assertEqual(largest(empty, 5), [])


class Cli(unittest.TestCase):
    def test_missing_directory_exits_2(self):
        self.assertEqual(main(["/nonexistent-path-xyz"]), 2)

    def test_zero_count_exits_2(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(main([d, "-n", "0"]), 2)

    def test_empty_directory_exits_1(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(main([d]), 1)
