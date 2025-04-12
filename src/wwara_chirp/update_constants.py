# This script is intended to be run as a GitHub Action to update the mock_chirp.py
# file in the wwara_chirp repository. It compares the constants in mock_chirp.py
# with those in chirp_common.py and updates them if necessary. If any updates are
# made, it creates a pull request to merge the changes into the dev branch.
import argparse
import logging
import os
import subprocess
import ast
from datetime import datetime
import json

from github import Github


class UpdateConstants:
    """
    The `UpdateConstants` class is responsible for automating the process of
    updating constants in a target file based on a source file from a GitHub
    repository.

    **Design Intent**:
    - This class is designed to be used in a CI/CD pipeline or as a standalone
      script.
    - It fetches files from GitHub, compares constants, and updates the target
      file if necessary.
    - It creates a new branch, commits the changes, and opens a pull request.
    - it was inspired by GitHub's dependabot-action
       https://github.com/github/dependabot-action

    **Responsibilities**:
    - Fetch files from GitHub repositories.
    - Compare constants between source and target files.
    - Update the target file with the latest constants.
    - Automate the Git workflow (branch creation, commit, pull request).

    **Design Decisions**:
    - Configuration is externalized in a JSON file for flexibility.
    - Uses the `PyGithub` library for GitHub API interactions.
    - Assumes the constants are stored in a dictionary-like structure for
      comparison.

    **Usage**:
    - Instantiate the class with a configuration file path.
    - Call the `main()` function to execute the update process.

    **Constraints**:
    - Requires a valid GitHub token in the environment variables.
    - Assumes the source and target files are compatible for comparison.
    """

    def __init__(self, config_path="config.json"):
        # Load configuration from JSON
        self.commit_sha = None
        with open(config_path, "r") as config_file:
            config = json.load(config_file)

        self.GITHUB_TOKEN = os.getenv(config["github_token_env"])
        self.WORKING_DIR = config["working_dir"]
        self.NEW_BRANCH_NAME = config["new_branch_name"]

        self.SOURCE_REPO = config["source"]["repo"]
        self.SOURCE_REPO_PATH = config["source"]["path"]
        self.SOURCE_BRANCH = config["source"]["branch"]
        self.SOURCE_FILE = config["source"]["file"]

        self.TARGET_REPO = config["target"]["repo"]
        self.TARGET_REPO_PATH = config["target"]["path"]
        self.TARGET_BRANCH = config["target"]["branch"]
        self.TARGET_FILE = config["target"]["file"]

        self.constants = {}
        self.github = Github(self.GITHUB_TOKEN)
        self.source_local_path = f"{self.WORKING_DIR}/{self.SOURCE_FILE}"
        self.target_local_path = f"{self.WORKING_DIR}/{self.TARGET_FILE}"
        self.prepare_working_directory()

    def check_for_updates(self, days=30):
        """
        Checks the SOURCE_REPO to see if the SOURCE_FILE has been updated
        within the last n days.

        :return: is_updated: bool
        """
        repo = self.github.get_repo(self.SOURCE_REPO)

        since_date = datetime(2024, 1, 1)
        commits = repo.get_commits(path=self.SOURCE_REPO_PATH, since=since_date)
        for commit in commits:
            if (commit.commit.author.date - commit.commit.committer.date).days <= days:
                return True
        return False


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


    @staticmethod
    def compare_and_update_constants(source_path, target_path, new_path):
        """
        Compares constants in two files and updates the target file with values
        from the source file if they differ.

        Args:
            source_path (str): Path to the source file.
            target_path (str): Path to the target file.
            new_path (str): Path to the new file to be created.

        Returns:
            bool: True if the target file was updated, False otherwise.
        """
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


    def commit_updates(self):
        """
        Commits the updated constants to a new branch in the target repository.

        This method creates a new branch, stages the updated constants, and commits
        the changes to the branch. The commit message includes details about the
        updated constants.

        Raises:
            github.GithubException: If there is an error during the branch creation
            or file update process.
        """

        # get the target repository
        target_repo = self.github.get_repo(self.TARGET_REPO)

        # Create the new branch
        target_branch = target_repo.get_branch(self.TARGET_BRANCH)
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

        self.commit_sha = new_branch.object.sha

    def create_pull_request(self):
        """
        Creates a pull request to merge the updated constants into the target branch.

        This method generates a pull request in the target repository, using the
        new branch created during the update process. The pull request includes a
        title and a detailed description of the changes made.

        Raises:
            github.GithubException: If there is an error during the pull request
            creation process.
        """

        repo = self.github.get_repo(self.TARGET_REPO)

        pr_title = "Update " + self.TARGET_FILE + " with latest constants from " + self.SOURCE_FILE
        pr_message = (
            "Update " + self.TARGET_FILE + " with latest constants from " +
            self.SOURCE_FILE + "\n\n" + "Updated constants:\n" + str(self.constants)
        )

        repo.create_pull(
            title=pr_title,
            body=pr_message,
            head=self.NEW_BRANCH_NAME,
            base=self.TARGET_BRANCH
        )


    def prepare_working_directory(self):
        """
        Prepares a clean working directory for the update process.
        """
        if os.path.exists(self.WORKING_DIR):
            subprocess.run(["rm", "-rf", self.WORKING_DIR])
        os.makedirs(self.WORKING_DIR)
        os.chdir(self.WORKING_DIR)


# ********************************************************************
# Main function to run the script
# ********************************************************************
def main():

    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting the update process")

    # use parse args to get the config file
    parser = argparse.ArgumentParser(description="Update constants in a file.")
    parser.add_argument(
        "--config", type=str, default="config.json",
        help="Path to the config file"
    )
    args = parser.parse_args()
    config_json = args.config

    print("Updating constants with latest values")
    updater = UpdateConstants(config_path=config_json)

    # Fetch files
    updater.fetch_file(updater.TARGET_REPO, updater.TARGET_FILE,
                       updater.TARGET_BRANCH)
    updater.fetch_file(updater.SOURCE_REPO, updater.SOURCE_FILE,
                       updater.SOURCE_BRANCH)

    # Compare and update constants
    updated = updater.compare_and_update_constants(
        updater.source_local_path, updater.target_local_path,
        updater.target_local_path
    )
    if updated:
        print("Constants updated. Committing changes...")
        updater.commit_updates()
        print("Changes committed. Creating pull request...")
        updater.create_pull_request()
        print("Pull request created.")
    else:
        print("No updates needed.")


if __name__ == "__main__":
    main()