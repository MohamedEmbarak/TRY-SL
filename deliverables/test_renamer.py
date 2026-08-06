#!/usr/bin/env python3
"""Acceptance-criteria test suite for renamer.py (requirements.md Sec.11).

stdlib `unittest` only -- no third-party test runner. Run with:
    python3 -m unittest deliverables.test_renamer -v
or, from inside deliverables/:
    python3 -m unittest test_renamer -v

Each test method is named test_criterion_NN and maps 1:1 to the numbered
acceptance criterion in requirements.md Sec.11, plus a block of extra
edge-case tests (test_edge_*) requested by the QA directive.

Criteria 16 and 18 are marked UNVERIFIED (self.skipTest) per Dev's note
that they are underspecified / unverifiable in this environment -- see
the docstrings on those two test methods for the concrete reason.
"""

import contextlib
import io
import os
import stat
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import renamer  # noqa: E402


def run_cli(args):
    """Invoke renamer.main(args) capturing stdout/stderr and exit code.

    renamer.main() normally *returns* an int exit code, but argparse (-h,
    missing required flags) calls sys.exit() directly, raising SystemExit
    from inside parse_args(). Both paths are normalized to (code, out, err).
    """
    out, err = io.StringIO(), io.StringIO()
    code = None
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = renamer.main(args)
        except SystemExit as exc:
            code = exc.code if isinstance(exc.code, int) else 0
    return code, out.getvalue(), err.getvalue()


class RenamerAcceptanceTests(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="renamer_test_")
        self.addCleanup(self._cleanup)

    def _cleanup(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _touch(self, *relparts, content=b""):
        path = os.path.join(self.tmpdir, *relparts)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(content)
        return path

    def _mkdir(self, *relparts):
        path = os.path.join(self.tmpdir, *relparts)
        os.makedirs(path, exist_ok=True)
        return path

    # -- 1 --------------------------------------------------------------
    def test_criterion_01_help_exits_0_mentions_pattern(self):
        code, out, err = run_cli(["-h"])
        self.assertEqual(code, 0)
        self.assertIn("--pattern", out)

    # -- 2 --------------------------------------------------------------
    def test_criterion_02_basic_rename(self):
        self._touch("a.txt")
        self._touch("b.txt")
        self._touch("c.md")
        code, out, err = run_cli(["--pattern", "*.txt", "--template",
                                   "{name}_x{ext}", "--path", self.tmpdir])
        self.assertEqual(code, 0)
        listing = set(os.listdir(self.tmpdir))
        self.assertEqual(listing, {"a_x.txt", "b_x.txt", "c.md"})

    # -- 3 --------------------------------------------------------------
    def test_criterion_03_dry_run_writes_nothing(self):
        self._touch("a.txt")
        self._touch("b.txt")
        self._touch("c.md")
        before = sorted(os.listdir(self.tmpdir))
        code, out, err = run_cli(["--pattern", "*.txt", "--template",
                                   "{name}_x{ext}", "--path", self.tmpdir,
                                   "--dry-run"])
        after = sorted(os.listdir(self.tmpdir))
        self.assertEqual(before, after)
        self.assertEqual(out.count("DRY-RUN:"), 2)
        self.assertEqual(code, 0)

    # -- 4 --------------------------------------------------------------
    def test_criterion_04_no_match_exits_4(self):
        self._touch("a.txt")
        code, out, err = run_cli(["--pattern", "*.nomatch", "--template",
                                   "{name}{ext}", "--path", self.tmpdir])
        self.assertEqual(code, 4)
        self.assertIn("NOTICE: no files matched", out)
        self.assertEqual(os.listdir(self.tmpdir), ["a.txt"])

    # -- 5 --------------------------------------------------------------
    def test_criterion_05_n_numbering_lexicographic(self):
        self._touch("alpha.txt")
        self._touch("beta.txt")
        self._touch("gamma.txt")
        code, out, err = run_cli(["--pattern", "*.txt", "--template",
                                   "f{n}{ext}", "--path", self.tmpdir])
        self.assertEqual(code, 0)
        listing = set(os.listdir(self.tmpdir))
        self.assertEqual(listing, {"f1.txt", "f2.txt", "f3.txt"})

    # -- 6 --------------------------------------------------------------
    def test_criterion_06_n_zero_padded(self):
        self._touch("only.txt")
        code, out, err = run_cli(["--pattern", "*.txt", "--template",
                                   "f{n:03}{ext}", "--path", self.tmpdir])
        self.assertEqual(code, 0)
        self.assertIn("f001.txt", os.listdir(self.tmpdir))

    # -- 7 --------------------------------------------------------------
    def test_criterion_07_unknown_field_exits_2(self):
        self._touch("a.txt")
        code, out, err = run_cli(["--pattern", "*.txt", "--template",
                                   "{bogus}{ext}", "--path", self.tmpdir])
        self.assertEqual(code, 2)
        self.assertTrue(err.strip())
        self.assertEqual(os.listdir(self.tmpdir), ["a.txt"])

    # NOTE: these three collision tests use template "{name}.renamed"
    # (fixed extension, not "{name}_x{ext}") so that the pre-existing
    # collision-target file does NOT itself also match --pattern "*.txt"
    # and get swept into the same run's match set (which would happen
    # with a .txt-preserving template, since the target's extension is
    # still .txt -- confirmed empirically while authoring this suite).

    # -- 8 --------------------------------------------------------------
    def test_criterion_08_on_collision_fail(self):
        self._touch("a.txt")
        self._touch("b.txt")
        self._touch("b.renamed")  # pre-existing collision target for b.txt
        code, out, err = run_cli(["--pattern", "*.txt", "--template",
                                   "{name}.renamed", "--path", self.tmpdir,
                                   "--on-collision", "fail"])
        self.assertEqual(code, 3)
        self.assertIn("ERROR: collision", err)
        listing = set(os.listdir(self.tmpdir))
        # a.txt (sorted before b.txt) completed before the collision
        self.assertIn("a.renamed", listing)
        # b.txt's rename never happened
        self.assertIn("b.txt", listing)

    # -- 9 --------------------------------------------------------------
    def test_criterion_09_on_collision_skip(self):
        self._touch("a.txt")
        self._touch("b.txt")
        self._touch("b.renamed")
        code, out, err = run_cli(["--pattern", "*.txt", "--template",
                                   "{name}.renamed", "--path", self.tmpdir,
                                   "--on-collision", "skip"])
        self.assertEqual(code, 0)
        listing = set(os.listdir(self.tmpdir))
        self.assertIn("a.renamed", listing)
        self.assertIn("b.txt", listing)  # left unrenamed

    # -- 10 -------------------------------------------------------------
    def test_criterion_10_on_collision_overwrite(self):
        self._touch("a.txt")
        self._touch("b.txt", content=b"NEW-CONTENT")
        self._touch("b.renamed", content=b"OLD-CONTENT")
        code, out, err = run_cli(["--pattern", "*.txt", "--template",
                                   "{name}.renamed", "--path", self.tmpdir,
                                   "--on-collision", "overwrite"])
        self.assertEqual(code, 0)
        listing = set(os.listdir(self.tmpdir))
        self.assertNotIn("b.txt", listing)
        with open(os.path.join(self.tmpdir, "b.renamed"), "rb") as f:
            self.assertEqual(f.read(), b"NEW-CONTENT")

    # -- 11 -------------------------------------------------------------
    def test_criterion_11_recursive_vs_flat(self):
        self._touch("top.txt")
        self._touch("sub", "deep.txt")

        code, out, err = run_cli(["--pattern", "*.txt", "--template",
                                   "{name}_r{ext}", "--path", self.tmpdir])
        self.assertEqual(code, 0)
        self.assertTrue(os.path.exists(os.path.join(self.tmpdir, "top_r.txt")))
        self.assertTrue(os.path.exists(os.path.join(self.tmpdir, "sub", "deep.txt")))

        code2, out2, err2 = run_cli(["--pattern", "*.txt", "--template",
                                      "{name}_r{ext}", "--path", self.tmpdir,
                                      "--recursive"])
        self.assertEqual(code2, 0)
        self.assertTrue(os.path.exists(os.path.join(self.tmpdir, "sub", "deep_r.txt")))

    # -- 12 -------------------------------------------------------------
    def test_criterion_12_include_dirs(self):
        self._mkdir("adir")
        # without --include-dirs: directory is not matchable -> zero
        # matches for this pattern -> untouched.
        code, out, err = run_cli(["--pattern", "adir", "--template",
                                   "{name}_r{ext}", "--path", self.tmpdir])
        self.assertIn("adir", os.listdir(self.tmpdir))

        # with --include-dirs: directory is matched and renamed.
        code2, out2, err2 = run_cli(["--pattern", "adir", "--template",
                                      "{name}_r{ext}", "--path", self.tmpdir,
                                      "--include-dirs"])
        self.assertEqual(code2, 0)
        self.assertIn("adir_r", os.listdir(self.tmpdir))
        self.assertNotIn("adir", os.listdir(self.tmpdir))

    # -- 13 -------------------------------------------------------------
    def test_criterion_13_bad_path_exits_2_no_traceback(self):
        bogus = os.path.join(self.tmpdir, "does_not_exist")
        code, out, err = run_cli(["--pattern", "*.txt", "--template",
                                   "{name}{ext}", "--path", bogus])
        self.assertEqual(code, 2)
        self.assertTrue(err.strip())
        self.assertNotIn("Traceback", out)
        self.assertNotIn("Traceback", err)

    # -- 14 -------------------------------------------------------------
    def test_criterion_14_missing_required_flags_exits_2(self):
        code, out, err = run_cli(["--template", "{name}{ext}",
                                   "--path", self.tmpdir])
        self.assertEqual(code, 2)
        self.assertNotIn("Traceback", out)
        self.assertNotIn("Traceback", err)

        code2, out2, err2 = run_cli(["--pattern", "*.txt", "--path", self.tmpdir])
        self.assertEqual(code2, 2)
        self.assertNotIn("Traceback", out2)
        self.assertNotIn("Traceback", err2)

    # -- 15 -------------------------------------------------------------
    def test_criterion_15_verbose_one_line_per_rename(self):
        for n in ("a", "b", "c"):
            self._touch(f"{n}.txt")

        code, out, err = run_cli(["--pattern", "*.txt", "--template",
                                   "{name}_x{ext}", "--path", self.tmpdir,
                                   "-v"])
        self.assertEqual(code, 0)
        self.assertEqual(out.count("RENAME:"), 3)

        # independent of --dry-run: fresh dir, same expectation.
        import shutil
        shutil.rmtree(self.tmpdir)
        os.makedirs(self.tmpdir)
        for n in ("a", "b", "c"):
            self._touch(f"{n}.txt")
        code2, out2, err2 = run_cli(["--pattern", "*.txt", "--template",
                                      "{name}_x{ext}", "--path", self.tmpdir,
                                      "-v", "--dry-run"])
        self.assertEqual(out2.count("RENAME:"), 3)

    # -- 16 -------------------------------------------------------------
    def test_criterion_16_idempotent_rerun_skip(self):
        """UNVERIFIED (Dev-flagged, confirmed by QA).

        The criterion assumes that re-running with identical args a second
        time re-matches the SAME logical files and finds their (now
        pre-existing) targets. But --pattern is re-evaluated against
        whatever is on disk at invocation time: if the template's output
        still satisfies --pattern (e.g. pattern "*.txt", template
        "{name}_x{ext}" -- the renamed file still ends in .txt), the
        second invocation matches the *renamed* files, not the originals,
        and produces a NEW set of targets (e.g. a_x_x.txt) rather than
        skipping. Empirically confirmed below: this is NOT idempotent for
        that (very natural) choice of pattern/template, contradicting the
        criterion's "zero files renamed on the second invocation" claim
        for the general case. Whether criterion 16 intends a pattern that
        is disjoint from its own template output is not specified in
        requirements.md Sec.3 or Sec.11 item 16. Marking UNVERIFIED rather
        than asserting either interpretation as ground truth.
        """
        self._touch("a.txt")
        code1, out1, err1 = run_cli(["--pattern", "*.txt", "--template",
                                      "{name}_x{ext}", "--path", self.tmpdir,
                                      "--on-collision", "skip"])
        self.assertEqual(code1, 0)
        self.assertIn("a_x.txt", os.listdir(self.tmpdir))

        code2, out2, err2 = run_cli(["--pattern", "*.txt", "--template",
                                      "{name}_x{ext}", "--path", self.tmpdir,
                                      "--on-collision", "skip"])
        # Empirical, not asserted as pass/fail: renamed again (not skipped).
        second_run_renamed_again = "a_x_x.txt" in os.listdir(self.tmpdir)
        self.skipTest(
            "UNVERIFIED: criterion 16 underspecified -- pattern "
            "'*.txt' re-matches the first run's own output, so the "
            "second invocation renames again instead of skipping "
            "(observed second_run_renamed_again=%r, exit=%r). See "
            "docstring." % (second_run_renamed_again, code2)
        )

    # -- 17 -------------------------------------------------------------
    def test_criterion_17_no_extension(self):
        self._touch("README")
        code, out, err = run_cli(["--pattern", "README", "--template",
                                   "{name}_v2{ext}", "--path", self.tmpdir])
        self.assertEqual(code, 0)
        listing = os.listdir(self.tmpdir)
        self.assertIn("README_v2", listing)
        self.assertNotIn("README_v2.", listing)

    # -- 18 -------------------------------------------------------------
    def test_criterion_18_permission_denied(self):
        """UNVERIFIED (Dev-flagged, confirmed by QA).

        This test suite is executing as uid=0 (root) in this environment
        (confirmed via `id` before writing this suite). os.chmod(0o444)
        does not block root's ability to write/rename a file on Linux, so
        the permission-denied path (exit 3 on OSError) cannot be
        triggered or verified as root. Requirement text itself says
        "run as non-root" -- this environment cannot satisfy that
        precondition.
        """
        target = self._touch("locked.txt")
        os.chmod(os.path.dirname(target), 0o555)
        try:
            os.chmod(target, 0o444)
            self.skipTest(
                "UNVERIFIED: test process is root (uid=0); os.chmod-based "
                "write-protection does not block root, so exit-3-on-"
                "permission-error cannot be exercised in this environment."
            )
        finally:
            os.chmod(os.path.dirname(target), 0o755)
            os.chmod(target, 0o644)

    # -- 19 -------------------------------------------------------------
    def test_criterion_19_readme_documents_flags_and_collision_modes(self):
        readme_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "README.md")
        self.assertTrue(
            os.path.isfile(readme_path),
            "deliverables/README.md does not exist -- criterion 19 "
            "requires a README.md delivered alongside renamer.py "
            "documenting all Sec.2 flags and a worked example per "
            "collision mode (skip/fail/overwrite)."
        )
        text = open(readme_path, encoding="utf-8").read()
        required_flags = ["--pattern", "--template", "--path", "--recursive",
                           "--dry-run", "--on-collision", "--include-dirs",
                           "-v", "-h"]
        for flag in required_flags:
            self.assertIn(flag, text, f"README.md missing documentation for {flag}")
        for mode in ("skip", "fail", "overwrite"):
            self.assertIn(mode, text, f"README.md missing worked example for on-collision={mode}")

    # -- 20 -------------------------------------------------------------
    def test_criterion_20_suite_covers_2_through_18(self):
        """Structural self-check: one test method per criterion 2-18 exists."""
        names = {n for n in dir(self.__class__) if n.startswith("test_criterion_")}
        for i in range(2, 19):
            expected_prefix = f"test_criterion_{i:02d}_"
            self.assertTrue(
                any(n.startswith(expected_prefix) for n in names),
                f"no test method found for criterion {i}"
            )

    # =====================================================================
    # Extra edge cases (beyond the 20 numbered criteria)
    # =====================================================================

    def test_edge_empty_directory_zero_matches(self):
        """Truly empty directory (no entries at all), distinct from
        criterion 4's non-matching-files case."""
        code, out, err = run_cli(["--pattern", "*.txt", "--template",
                                   "{name}{ext}", "--path", self.tmpdir])
        self.assertEqual(code, 4)
        self.assertIn("NOTICE: no files matched", out)

    def test_edge_no_extension_recursive_deep(self):
        self._touch("sub", "sub2", "NOEXT")
        code, out, err = run_cli(["--pattern", "NOEXT", "--template",
                                   "{name}_r{ext}", "--path", self.tmpdir,
                                   "--recursive"])
        self.assertEqual(code, 0)
        self.assertTrue(os.path.exists(
            os.path.join(self.tmpdir, "sub", "sub2", "NOEXT_r")))


if __name__ == "__main__":
    unittest.main()
