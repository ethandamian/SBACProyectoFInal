import os
import shutil
import unittest
from src.classes.sbac import SBAC

class TestIntegrationSBAC(unittest.TestCase):
    def setUp(self):
        # Create a clean test environment
        self.repo_path = "test_repo"
        os.makedirs(self.repo_path, exist_ok=True)
        os.chdir(self.repo_path)

        self.sbac = SBAC()

        # Create test files
        with open("file1.txt", "w") as f:
            f.write("Content of file 1.")
        with open("file2.txt", "w") as f:
            f.write("Content of file 2.")

    def tearDown(self):
        # Return to previous directory and remove test repo
        os.chdir("..")
        shutil.rmtree(self.repo_path)

    def test_full_flow(self):
        # Initialize repo
        self.assertTrue(self.sbac.init())
        self.assertTrue(os.path.isdir(".sbac"))

        # Add files
        self.assertTrue(self.sbac.add(["file1.txt", "file2.txt"]))
        index_path = os.path.join(".sbac", "index")
        self.assertTrue(os.path.exists(index_path))

        # Commit changes
        commit_msg = "First commit"
        self.assertTrue(self.sbac.commit(commit_msg))

        # Check log
        self.assertTrue(self.sbac.log())

        # Add an untracked file
        with open("file3.txt", "w") as f:
            f.write("Untracked file.")
        self.assertTrue(self.sbac.status())

        # Create new branch
        self.assertTrue(self.sbac.create_branch("feature"))

    def test_commit_without_add(self):
        self.sbac.init()
        result = self.sbac.commit("Attempt without add")
        self.assertFalse(result)

    def test_add_nonexistent_file(self):
        self.sbac.init()
        result = self.sbac.add(["does_not_exist.txt"])
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()
