import contextlib
import io
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import loc  # noqa: E402


def write(path, content="", binary=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if binary:
        with open(path, "wb") as f:
            f.write(content)
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)


class TestLoc(unittest.TestCase):
    def setUp(self):
        self.tmp_path = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp_path, ignore_errors=True)

    def run_main(self, args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = loc.main(args)
        return rc, out.getvalue(), err.getvalue()

    def test_empty_directory(self):
        rc, out, err = self.run_main([self.tmp_path])
        self.assertEqual(rc, 0)
        self.assertIn("TOTAL", out)
        # no extension rows besides header/total separators
        self.assertIn("0", out.splitlines()[-1])

    def test_nested_tree(self):
        write(os.path.join(self.tmp_path, "a.py"), "line1\nline2\nline3\n")
        write(os.path.join(self.tmp_path, "sub", "b.py"), "x\ny\n")
        write(os.path.join(self.tmp_path, "sub", "deep", "c.js"), "one\ntwo\nthree\nfour\n")

        rc, out, err = self.run_main([self.tmp_path])
        self.assertEqual(rc, 0)

        lines = out.splitlines()
        py_line = next(l for l in lines if l.strip().startswith(".py"))
        js_line = next(l for l in lines if l.strip().startswith(".js"))
        total_line = next(l for l in lines if l.strip().startswith("TOTAL"))

        self.assertEqual(py_line.split()[1], "2")   # 2 .py files
        self.assertEqual(py_line.split()[2], "5")   # 3 + 2 lines
        self.assertEqual(js_line.split()[1], "1")
        self.assertEqual(js_line.split()[2], "4")
        self.assertEqual(total_line.split()[1], "3")
        self.assertEqual(total_line.split()[2], "9")
        # .py has more lines than .js, so it should be listed first
        self.assertLess(lines.index(py_line), lines.index(js_line))

    def test_git_dir_is_skipped(self):
        write(os.path.join(self.tmp_path, ".git", "config"), "should not be counted\n" * 5)
        write(os.path.join(self.tmp_path, "real.py"), "a\nb\n")

        rc, out, err = self.run_main([self.tmp_path])
        self.assertEqual(rc, 0)
        self.assertNotIn("config", out)
        total_line = next(l for l in out.splitlines() if l.strip().startswith("TOTAL"))
        self.assertEqual(total_line.split()[1], "1")
        self.assertEqual(total_line.split()[2], "2")

    def test_ext_filter(self):
        write(os.path.join(self.tmp_path, "a.py"), "1\n2\n")
        write(os.path.join(self.tmp_path, "b.js"), "1\n2\n3\n")
        write(os.path.join(self.tmp_path, "c.md"), "1\n")

        rc, out, err = self.run_main([self.tmp_path, "--ext", ".py,.js"])
        self.assertEqual(rc, 0)
        self.assertIn(".py", out)
        self.assertIn(".js", out)
        self.assertNotIn(".md", out)

    def test_top_limit(self):
        write(os.path.join(self.tmp_path, "a.py"), "1\n" * 10)
        write(os.path.join(self.tmp_path, "b.js"), "1\n" * 5)
        write(os.path.join(self.tmp_path, "c.md"), "1\n" * 1)

        rc, out, err = self.run_main([self.tmp_path, "--top", "1"])
        self.assertEqual(rc, 0)
        self.assertIn(".py", out)
        self.assertNotIn(".js", out)
        self.assertNotIn(".md", out)
        # TOTAL still reflects only the shown groups' sum in the table body,
        # but files/lines total is computed over all files, not just top N.
        total_line = next(l for l in out.splitlines() if l.strip().startswith("TOTAL"))
        self.assertEqual(total_line.split()[1], "3")
        self.assertEqual(total_line.split()[2], "16")

    def test_extensionless_files(self):
        write(os.path.join(self.tmp_path, "README"), "hello\nworld\n")
        write(os.path.join(self.tmp_path, "Makefile"), "build:\n\techo hi\n")

        rc, out, err = self.run_main([self.tmp_path])
        self.assertEqual(rc, 0)
        self.assertIn("(none)", out)
        none_line = next(l for l in out.splitlines() if l.strip().startswith("(none)"))
        self.assertEqual(none_line.split()[1], "2")
        self.assertEqual(none_line.split()[2], "4")

    def test_binary_file_skipped(self):
        write(os.path.join(self.tmp_path, "image.bin"), b"\x00\x01\x02binarydata\xff\xfe", binary=True)
        write(os.path.join(self.tmp_path, "text.py"), "print('hi')\n")

        rc, out, err = self.run_main([self.tmp_path])
        self.assertEqual(rc, 0)
        self.assertNotIn(".bin", out)
        total_line = next(l for l in out.splitlines() if l.strip().startswith("TOTAL"))
        self.assertEqual(total_line.split()[1], "1")
        self.assertEqual(total_line.split()[2], "1")

    def test_bad_path_nonexistent(self):
        missing = os.path.join(self.tmp_path, "does_not_exist")
        rc, out, err = self.run_main([missing])
        self.assertNotEqual(rc, 0)
        self.assertIn("does not exist", err)

    def test_bad_path_not_a_directory(self):
        file_path = os.path.join(self.tmp_path, "just_a_file.txt")
        write(file_path, "hi\n")

        rc, out, err = self.run_main([file_path])
        self.assertNotEqual(rc, 0)
        self.assertIn("not a directory", err)


if __name__ == "__main__":
    unittest.main()
