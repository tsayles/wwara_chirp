import requests
import getpass

# GitHub repository details
repo_owner = "tsayles"
repo_name = "wwara_chirp"
token = getpass.getpass("Enter your GitHub token: ")  # Prompt for the token

# Headers for authentication
headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json"
}

# Create the main issue
main_issue = {
    "title": "Plan for Project Updates",
    "body": """
### Plan for Project Updates

1. **Directly Include the `chirp` Dependencies**
2. **Automatically Generate Pull Requests for Relevant Updates**
3. **Automated Testing of Locally Included `chirp` Elements**
4. **Associated Documentation Updates**
5. **GitHub Release as v2.0.4**
"""
}

response = requests.post(
    f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues",
    headers=headers,
    json=main_issue
)

if response.status_code == 201:
    main_issue_number = response.json()["number"]
else:
    print(f"Failed to create main issue: {response.status_code}")
    print(response.json())
    exit(1)

# Create sub-issues
sub_issues = [
    {
        "title": "Directly Include the `chirp` Dependencies",
        "body": "Clone the `chirp` repository into a subdirectory and update import paths.",
        "labels": ["enhancement"],
        "assignees": ["tsayles"]
    },
    {
        "title": "Automatically Generate Pull Requests for Relevant Updates",
        "body": "Set up a GitHub Action to periodically check for updates in the `kk7ds/chirp` repository.",
        "labels": ["enhancement"],
        "assignees": ["tsayles"]
    },
    {
        "title": "Automated Testing of Locally Included `chirp` Elements",
        "body": "Add tests to ensure the locally included `chirp` elements work correctly with the project.",
        "labels": ["enhancement"],
        "assignees": ["tsayles"]
    },
    {
        "title": "Associated Documentation Updates",
        "body": "Update the documentation to reflect the inclusion of the `chirp` code.",
        "labels": ["documentation"],
        "assignees": ["tsayles"]
    },
    {
        "title": "GitHub Release as v2.0.4",
        "body": "Update the version number to v2.0.4 and create a GitHub release.",
        "labels": ["release"],
        "assignees": ["tsayles"]
    }
]

for sub_issue in sub_issues:
    sub_issue["body"] += f"\n\nParent issue: #{main_issue_number}"
    response = requests.post(
        f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues",
        headers=headers,
        json=sub_issue
    )
    if response.status_code != 201:
        print(f"Failed to create sub-issue: {response.status_code}")
        print(response.json())