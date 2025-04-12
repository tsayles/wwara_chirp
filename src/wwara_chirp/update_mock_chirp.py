# This script is intended to be run as a GitHub Action to update the mock_chirp.py
# file in the wwara_chirp repository. It compares the constants in mock_chirp.py
# with those in chirp_common.py and updates them if necessary. If any updates are
# made, it creates a pull request to merge the changes into the dev branch.
import logging
import os
import subprocess
import ast
import requests

from github import Github
from numpy.f2py.crackfortran import sourcecodeform


class UpdateConstants:
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    WORKING_DIR = "updater"
    NEW_BRANCH_NAME = "update-constants"

    # SOURCE_URL = "https://raw.githubusercontent.com/kk7ds/chirp/refs/heads/master/chirp/chirp_common.py"
    SOURCE_REPO = "kk7ds/chirp"
    SOURCE_BRANCH = "master"
    SOURCE_FILE = "chirp_common.py"
    SOURCE_REPO_PATH = "chirp/chirp_common.py"

    # REPO_URL = "https://github.com/tsayles/wwara_chirp.git"
    REPO_NAME = "tsayles/wwara_chirp"
    BASE_BRANCH = "dev"
    TARGET_FILE = "mock_chirp.py"
    TARGET_REPO_PATH = "src/wwara_chirp/mock_chirp.py"

    def __init__(self):
        self.constants = {}
        self.github = Github(self.GITHUB_TOKEN)
        self.source_local_path = os.path.join(self.WORKING_DIR, self.SOURCE_FILE)
        self.target_local_path = os.path.join(self.WORKING_DIR, self.TARGET_FILE)


    def fetch_file(self, repo_name, file_name, branch):
        """
        Fetches a file from a GitHub repository and writes it locally.

        Args:
            repo_name (str): The name of the repository (e.g., "owner/repo").
            file_name (str): The name of the file to fetch.
            branch (str): The branch to fetch the file from.

        Returns:
            str: The content of the fetched file.
        """
        repo = self.github.get_repo(repo_name)
        contents = repo.get_contents(file_name, ref=branch).decoded_content
        with open(file_name, "w") as file:
            file.write(contents)

        logging.debug(f"Fetched {file_name} from {repo_name}")
        logging.debug(contents)

        return contents

    def fetch_files(self):
        """
        Fetches both mock_chirp.py and chirp_common.py files.
        """
        mock_chirp_content = self.fetch_file(self.REPO_NAME, self.TARGET_FILE, self.BASE_BRANCH)
        chirp_common_content = self.fetch_file(self.SOURCE_REPO, self.SOURCE_FILENAME, "master")
        return mock_chirp_content, chirp_common_content


    def compare_and_update_constants(self, source_path, target_path, new_path):
        with open(source_path, 'r') as source_file:
            source_constants = ast.literal_eval(source_file.read())

        with open(target_path, 'r') as target_file:
            target_constants = ast.literal_eval(target_file.read())

        updated = False
        for key, value in source_constants.items():
            if key in target_constants and target_constants[key] != value:
                target_constants[key] = value
                updated = True

        if updated:
            with open(new_path, 'w') as new_file:
                new_file.write(str(target_constants))

        return updated



    def commit_and_create_pr(self):
        # subprocess.run(["git", "config", "--global", "user.name", "github-actions[bot]"])
        # subprocess.run(["git", "config", "--global", "user.email", "github-actions[bot]@users.noreply.github.com"])
        # subprocess.run(["git", "checkout", "-b", self.BRANCH_NAME])
        # subprocess.run(["git", "add", "src/wwara_chirp/mock_chirp.py"])
        # subprocess.run(["git", "commit", "-m", "Update mock_chirp.py with latest constants from chirp_common.py"])
        # subprocess.run(["git", "push", "origin", self.BRANCH_NAME])

        # get the target repository
        target_repo = self.github.get_repo(self.REPO_NAME)

        # Create the new branch
        target_branch = target_repo.get_branch(self.BASE_BRANCH)
        new_branch = target_repo.create_git_ref(ref=f"refs/heads/{self.NEW_BRANCH_NAME}", sha=target_branch.commit.sha)

        # Commit the changes

        commit_message = (
            "Update " + self.TARGET_FILE + " with latest constants from " +
            self.SOURCE_FILE + "\n\n" + "Updated constants:\n" + str(self.constants)
        )

        with open(self.target_local_path, 'r') as file:
            content = file.read()

        target_repo.update_file(
            path=self.TARGET_REPO_PATH,
            message= commit_message,
            content=content,
            sha=new_branch.object.sha,
            branch=self.NEW_BRANCH_NAME
        )

        self.commit

    def create_pull_request(self):
        # Create a pull request

        repo = self.github.get_repo(self.REPO_NAME)
        repo.create_pull(
            title="Update mock_chirp.py with latest constants",
            body="This PR updates mock_chirp.py with the latest constants from chirp_common.py",
            head=self.NEW_BRANCH_NAME,
            base=self.BASE_BRANCH
        )

def main():
    print("Updating mock_chirp.py with latest constants")
    updater = UpdateConstants()

    # Check if the script is being run in the correct directory
    pwd = os.getcwd()
    print(f"Current working directory: {pwd}")

    # Create a clean {{repo}}/updater directory for the update process
    if os.path.exists("updater"):
        subprocess.run(["rm", "-rf", "updater"])
    os.makedirs("updater")
    os.chdir("updater")

    updater.clone_repo()
    updater.download_chirp_common()
    common_constants = updater.parse_constants()
    mock_constants = updater.parse_mock_chirp()
    updated, updated_mock_constants = updater.compare_constants(common_constants, mock_constants)
    if updated:
        updater.update_mock_chirp(updated_mock_constants)
        updater.commit_and_create_pr()
    else:
        print("No updates needed. mock_chirp.py is already up to date.")

    # Clean up the updater directory
    os.chdir("..")
    subprocess.run(["rm", "-rf", "updater"])


if __name__ == "__main__":
    main()