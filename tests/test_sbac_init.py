import unittest
import tempfile
import os
import shutil
from types import SimpleNamespace

from src.commands.init import cmd_init
from src.repository import GitRepository

class TestSbacCmdInit(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_cmd_init_creates_git_structure(self):
        args = SimpleNamespace(path=self.test_dir)
        cmd_init(args)

        git_dir = os.path.join(self.test_dir, ".git")
        self.assertTrue(os.path.isdir(git_dir), ".git directory should exist")

        expected_dirs = [
            "branches",
            "objects",
            "refs/tags",
            "refs/heads"
        ]

        for d in expected_dirs:
            path = os.path.join(git_dir, d)
            self.assertTrue(os.path.isdir(path), f"Expected directory {path} not found")

        expected_files = [
            "description",
            "HEAD",
            "config"
        ]

        for f in expected_files:
            path = os.path.join(git_dir, f)
            self.assertTrue(os.path.isfile(path), f"Expected file {path} not found")

    def test_cmd_init_writes_correct_config(self):
        args = SimpleNamespace(path=self.test_dir)
        cmd_init(args)

        repo = GitRepository(self.test_dir)
        config = repo.conf

        self.assertEqual(config.get("core", "repositoryformatversion"), "0")
        self.assertEqual(config.get("core", "filemode"), "false")
        self.assertEqual(config.get("core", "bare"), "false")

    def test_cmd_init_fails_on_non_empty_repo(self):
        # Creamos .git y metemos un archivo ahí
        os.makedirs(os.path.join(self.test_dir, ".git"))
        with open(os.path.join(self.test_dir, ".git", "dummy.txt"), "w") as f:
            f.write("data")

        args = SimpleNamespace(path=self.test_dir)
        with self.assertRaises(Exception):
            cmd_init(args)

if __name__ == "__main__":
    unittest.main()
