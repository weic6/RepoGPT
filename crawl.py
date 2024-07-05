import re
import requests
import base64


def extract_owner_repo(url):
    pattern = r"github\.com/([^/]+)/([^/]+)"
    match = re.search(pattern, url)
    if match:
        owner, repo = match.groups()
        repo = repo.split("/")[0]
        # print(f"Owner: {owner}, Repo: {repo}")
        return owner, repo
    return None, None


def get_repo_contents(owner, repo, path="", github_token=None):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {"Authorization": f"token {github_token}"} if github_token else {}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def crawl_repo(owner, repo, github_token=None):
    all_files = []

    def crawl_path(path):
        contents = get_repo_contents(owner, repo, path, github_token)
        for item in contents:
            if (
                item["name"].startswith(".")
                or item["name"].startswith("_")
                or item["name"] in ["LICENSE"]
            ):
                continue
            # print(item)
            if item["type"] == "file":
                all_files.append(item["path"])
            elif item["type"] == "dir":
                crawl_path(item["path"])

    crawl_path("")
    # print(all_files)
    return all_files


def fetch_file_content(owner, repo, file_path, github_token=None):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
    headers = {"Authorization": f"token {github_token}"} if github_token else {}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    # print(response.json())
    content = response.json()["content"]
    return base64.b64decode(content).decode("utf-8")
