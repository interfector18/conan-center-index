import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from select_recipes import select_recipes
from verify_recipe_publication import verify


class RecipeSelectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.name", "Publication test")
        self.git("config", "user.email", "test@example.invalid")
        self.write_recipe("libiconv", "old recipe")
        self.write_recipe("unchanged", "same recipe")
        self.baseline = self.commit("published")
        self.history = [{"workflow_runs": [self.workflow_run(10, self.baseline)]}]

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, text=True).strip()

    def write_recipe(self, name, content):
        directory = self.root / "recipes" / name
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "config.yml").write_text("versions: {}\n")
        (directory / "conanfile.py").write_text(content)

    def commit(self, message):
        self.git("add", ".")
        self.git("commit", "-qm", message)
        return self.git("rev-parse", "HEAD")

    @staticmethod
    def workflow_run(run_id, sha, event="push", conclusion="success", branch="master"):
        return {"id": run_id, "head_sha": sha, "event": event,
                "conclusion": conclusion, "head_branch": branch}

    def select(self, recipe=""):
        return select_recipes(self.root, self.history, 20, "master", recipe)

    def test_upstream_update_is_selected_even_when_identical_to_upstream(self):
        self.write_recipe("libiconv", "new upstream recipe")
        self.commit("merge upstream")
        self.git("branch", "upstream/master")
        # The previous workflow sees no changes in this exact scenario.
        self.assertEqual(self.git("diff", "--name-only", "upstream/master", "--", "recipes/"), "")
        self.assertEqual(self.select(), ["libiconv"])

    def test_failed_and_targeted_manual_runs_do_not_advance_baseline(self):
        self.write_recipe("libiconv", "new recipe")
        updated = self.commit("unpublished update")
        self.history[0]["workflow_runs"] += [
            self.workflow_run(11, updated, conclusion="failure"),
            self.workflow_run(12, updated, event="workflow_dispatch"),
            self.workflow_run(13, updated, branch="other"),
            self.workflow_run(20, updated), self.workflow_run(21, updated),
        ]
        self.assertEqual(self.select(), ["libiconv"])

    def test_latest_successful_push_across_pages_is_baseline(self):
        self.write_recipe("libiconv", "published update")
        updated = self.commit("published update")
        self.history.append({"workflow_runs": [self.workflow_run(15, updated)]})
        self.write_recipe("new", "new recipe")
        self.commit("new package")
        self.assertEqual(self.select(), ["new"])

    def test_no_history_or_missing_commit_selects_all(self):
        for history in ([], [{"workflow_runs": [self.workflow_run(10, "0" * 40)]}]):
            self.history = history
            self.assertEqual(self.select(), ["libiconv", "unchanged"])

    def test_deleted_recipe_is_not_exported(self):
        self.git("rm", "-r", "recipes/libiconv")
        self.commit("remove recipe")
        self.assertEqual(self.select(), [])

    def test_manual_recipe_is_validated(self):
        self.assertEqual(self.select("unchanged"), ["unchanged"])
        for name in ("missing", "../recipes", "libiconv; echo unsafe"):
            with self.assertRaises(ValueError):
                self.select(name)


class RemoteVerificationTests(unittest.TestCase):
    @patch("verify_recipe_publication.subprocess.run")
    def test_conan_success_exit_with_json_error_still_fails(self, run):
        run.return_value.stdout = json.dumps({"remote": {"error": "Revision not found"}})
        with self.assertRaisesRegex(RuntimeError, "Missing published revision"):
            verify("remote", "libiconv/1.17#required")

    @patch("verify_recipe_publication.subprocess.run")
    def test_other_revision_does_not_satisfy_export(self, run):
        run.return_value.stdout = json.dumps({"remote": {"libiconv/1.17": {"revisions": {"old": {}}}}})
        with self.assertRaises(RuntimeError):
            verify("remote", "libiconv/1.17#required")

    @patch("verify_recipe_publication.subprocess.run")
    def test_exact_revision_passes(self, run):
        run.return_value.stdout = json.dumps({"remote": {"libiconv/1.17": {"revisions": {"required": {}}}}})
        verify("remote", "libiconv/1.17#required")


if __name__ == "__main__":
    unittest.main()
