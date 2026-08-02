# This script is intended to be run as a GitHub Action to update the
# mock_chirp.py file in the wwara_chirp repository. It compares the
# constants in mock_chirp.py with those in chirp_common.py and updates
# them if necessary. If any updates are made, it creates a pull request
# to merge the changes into the dev branch.

import ast
import os
import subprocess

import requests
from github import Github


class UpdateMockChirp:
    REPO_URL = "https://github.com/tsayles/wwara_chirp.git"
    CHIRP_COMMON_URL = (
        "https://raw.githubusercontent.com/kk7ds/chirp/refs/heads/master/"
        "chirp/chirp_common.py"
    )
    CHIRP_COMMON_FILENAME = "chirp_common.py"
    MOCK_CHIRP_FILENAME = "src/wwara_chirp/mock_chirp.py"
    BRANCH_NAME = "update-mock-chirp"
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    REPO_NAME = "tsayles/wwara_chirp"
    BASE_BRANCH = "dev"
    MOCK_CHIRP_CLASS_NAME = "MockChirp"

    def __init__(self):
        self.constants = {}

    def clone_repo(self):
        subprocess.run(["git", "clone", self.REPO_URL], check=True)
        os.chdir("wwara_chirp")
        subprocess.run(["git", "checkout", self.BASE_BRANCH], check=True)
        subprocess.run(["git", "pull", "origin", self.BASE_BRANCH], check=True)

    def download_chirp_common(self):
        response = requests.get(self.CHIRP_COMMON_URL, timeout=30)
        response.raise_for_status()
        with open(self.CHIRP_COMMON_FILENAME, "w", encoding="utf-8") as file:
            file.write(response.text)

    @staticmethod
    def _parse_uppercase_assignments(tree):
        constants = {}
        for node in tree.body:
            if not isinstance(node, ast.Assign) or len(node.targets) != 1:
                continue
            target = node.targets[0]
            if not isinstance(target, ast.Name) or not target.id.isupper():
                continue
            try:
                constants[target.id] = ast.literal_eval(node.value)
            except ValueError:
                continue
        return constants

    @staticmethod
    def _get_mock_chirp_class(tree):
        for node in tree.body:
            if (
                isinstance(node, ast.ClassDef)
                and node.name == UpdateMockChirp.MOCK_CHIRP_CLASS_NAME
            ):
                return node
        raise ValueError("MockChirp class not found in mock_chirp.py")

    def parse_chirp_common(self):
        with open(self.CHIRP_COMMON_FILENAME, "r", encoding="utf-8") as file:
            chirp_common = ast.parse(file.read(), self.CHIRP_COMMON_FILENAME)
        return self._parse_uppercase_assignments(chirp_common)

    def parse_mock_chirp(self):
        with open(self.MOCK_CHIRP_FILENAME, "r", encoding="utf-8") as file:
            mock_chirp = ast.parse(file.read(), self.MOCK_CHIRP_FILENAME)
        mock_chirp_class = self._get_mock_chirp_class(mock_chirp)
        return self._parse_uppercase_assignments(mock_chirp_class)

    def compare_constants(self, common_constants, mock_constants):
        updated = False
        updated_mock_constants = dict(mock_constants)
        for key, mock_value in mock_constants.items():
            if key not in common_constants:
                continue
            common_value = common_constants[key]
            if mock_value != common_value:
                updated_mock_constants[key] = common_value
                updated = True
        return updated, updated_mock_constants

    def update_mock_chirp(self, mock_constants):
        with open(self.MOCK_CHIRP_FILENAME, "r", encoding="utf-8") as file:
            source = file.read()

        tree = ast.parse(source, self.MOCK_CHIRP_FILENAME)
        mock_chirp_class = self._get_mock_chirp_class(tree)
        replacements = []
        lines = source.splitlines(keepends=True)

        for node in mock_chirp_class.body:
            if not isinstance(node, ast.Assign) or len(node.targets) != 1:
                continue
            target = node.targets[0]
            if (
                not isinstance(target, ast.Name)
                or target.id not in mock_constants
            ):
                continue
            start_line = node.lineno - 1
            end_line = node.end_lineno
            start = sum(len(line) for line in lines[:start_line])
            end = sum(len(line) for line in lines[:end_line])
            indent = " " * node.col_offset
            replacement = (
                f"{indent}{target.id} = "
                f"{repr(mock_constants[target.id])}\n"
            )
            replacements.append((start, end, replacement))

        for start, end, replacement in reversed(replacements):
            source = source[:start] + replacement + source[end:]

        with open(self.MOCK_CHIRP_FILENAME, "w", encoding="utf-8") as file:
            file.write(source)

    def commit_and_create_pr(self):
        subprocess.run(
            ["git", "config", "--global", "user.name", "github-actions[bot]"],
            check=True,
        )
        subprocess.run(
            [
                "git",
                "config",
                "--global",
                "user.email",
                "github-actions[bot]@users.noreply.github.com",
            ],
            check=True,
        )
        subprocess.run(["git", "checkout", "-b", self.BRANCH_NAME], check=True)
        subprocess.run(["git", "add", self.MOCK_CHIRP_FILENAME], check=True)
        subprocess.run(
            [
                "git",
                "commit",
                "-m",
                "Update mock_chirp.py with latest constants from "
                "chirp_common.py",
            ],
            check=True,
        )
        subprocess.run(["git", "push", "origin", self.BRANCH_NAME], check=True)

        g = Github(self.GITHUB_TOKEN)
        repo = g.get_repo(self.REPO_NAME)
        repo.create_pull(
            title="Update mock_chirp.py with latest constants",
            body=(
                "This PR updates mock_chirp.py with the latest constants "
                "from chirp_common.py"
            ),
            head=self.BRANCH_NAME,
            base=self.BASE_BRANCH,
        )


def main():
    print("Updating mock_chirp.py with latest constants")
    updater = UpdateMockChirp()

    pwd = os.getcwd()
    print(f"Current working directory: {pwd}")

    if os.path.exists("updater"):
        subprocess.run(["rm", "-rf", "updater"], check=True)
    os.makedirs("updater")
    os.chdir("updater")

    updater.clone_repo()
    updater.download_chirp_common()
    common_constants = updater.parse_chirp_common()
    mock_constants = updater.parse_mock_chirp()
    updated, updated_mock_constants = updater.compare_constants(
        common_constants,
        mock_constants,
    )
    if updated:
        updater.update_mock_chirp(updated_mock_constants)
        updater.commit_and_create_pr()
    else:
        print("No updates needed. mock_chirp.py is already up to date.")

    os.chdir("..")
    subprocess.run(["rm", "-rf", "updater"], check=True)


if __name__ == "__main__":
    main()
