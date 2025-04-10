# This script is intended to be run as a GitHub Action to update the mock_chirp.py
# file in the wwara_chirp repository. It compares the constants in mock_chirp.py
# with those in chirp_common.py and updates them if necessary. If any updates are
# made, it creates a pull request to merge the changes into the dev branch.

import os
import subprocess
import ast
import requests
from github import Github

class UpdateMockChirp:
    REPO_URL = "https://github.com/tsayles/wwara_chirp.git"
    CHIRP_COMMON_URL = "https://raw.githubusercontent.com/kk7ds/chirp/refs/heads/master/chirp/chirp_common.py"
    CHIRP_COMMON_FILENAME = "chirp_common.py"
    MOCK_CHIRP_FILENAME = "src/wwara_chirp/mock_chirp.py"
    BRANCH_NAME = "update-mock-chirp"
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    REPO_NAME = "tsayles/wwara_chirp"
    BASE_BRANCH = "dev"

    def __init__(self):
        self.constants = {}

    def clone_repo(self):
        subprocess.run(["git", "clone", self.REPO_URL])
        os.chdir("wwara_chirp")
        subprocess.run(["git", "checkout", self.BASE_BRANCH])
        subprocess.run(["git", "pull", "origin", self.BASE_BRANCH])

    def download_chirp_common(self):
        response = requests.get(self.CHIRP_COMMON_URL)
        with open(self.CHIRP_COMMON_FILENAME, "w") as file:
            file.write(response.text)

    def parse_chirp_common(self):
        # Open 'chirp_common.py' and read its contents
        with open(self.CHIRP_COMMON_FILENAME, "r") as file:
            chirp_common = file.read()

        # Create a controlled environment for execution
        local_vars = {}
        exec(chirp_common, {}, local_vars)

        # Filter out constants (uppercase variable names)
        chirp_common_constants = {
            key: value for key, value in local_vars.items() if key.isupper()
        }

        return chirp_common_constants

    def parse_mock_chirp(self):
        # Open 'src/wwara_chirp/mock_chirp.py' and read its contents
        # with open("src/wwara_chirp/mock_chirp.py", "r") as file:
        with open(self.MOCK_CHIRP_FILENAME, "r") as file:
            mock_chirp = file.read()
        # Parse the contents of 'mock_chirp.py' as a dictionary
        mock_constants = ast.literal_eval(mock_chirp)
        # Filter constants that are uppercase from mock_constants
        return {k: v for k, v in mock_constants.items() if k.isupper()}

    def compare_constants(self, common_constants, mock_constants):
        updated = False
        # Iterate over the items in common_constants
        for key, value in common_constants.items():
            # Check if the key exists in mock_constants and if the values are different
            if key in mock_constants and mock_constants[key] != value:
                # Update the value in mock_constants to match the value in common_constants
                mock_constants[key] = value
                updated = True
            # If the key does not exist in mock_constants, add it
            elif key not in mock_constants:
                mock_constants[key] = value
                updated = True
        return updated, mock_constants

    def update_mock_chirp(self, mock_constants):
        # Write the updated mock_constants back to 'mock_chirp.py'
        with open(self.MOCK_CHIRP_FILENAME, "w") as file:
            file.write(str(mock_constants))

    def commit_and_create_pr(self):
        subprocess.run(["git", "config", "--global", "user.name", "github-actions[bot]"])
        subprocess.run(["git", "config", "--global", "user.email", "github-actions[bot]@users.noreply.github.com"])
        subprocess.run(["git", "checkout", "-b", self.BRANCH_NAME])
        subprocess.run(["git", "add", "src/wwara_chirp/mock_chirp.py"])
        subprocess.run(["git", "commit", "-m", "Update mock_chirp.py with latest constants from chirp_common.py"])
        subprocess.run(["git", "push", "origin", self.BRANCH_NAME])

        g = Github(self.GITHUB_TOKEN)
        repo = g.get_repo(self.REPO_NAME)
        repo.create_pull(
            title="Update mock_chirp.py with latest constants",
            body="This PR updates mock_chirp.py with the latest constants from chirp_common.py",
            head=self.BRANCH_NAME,
            base=self.BASE_BRANCH
        )

def main():
    print("Updating mock_chirp.py with latest constants")
    updater = UpdateMockChirp()

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
    common_constants = updater.parse_chirp_common()
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