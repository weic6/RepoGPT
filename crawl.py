import re
import requests
import base64
import os
import chardet


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


def crawl_local_repo(repo_path, rel_path=False):
    all_files = []
    for root, dirs, files in os.walk(repo_path):
        # print(root, dirs, files)
        # Filter out directories starting with '.' and filter out "pycache"
        dirs[:] = [d for d in dirs if not d.startswith(".") and not d.startswith("_")]

        for file in files:
            if file.startswith(".") or file.startswith("_") or file in ["LICENSE"]:
                continue
            if any(
                file.endswith(ext)
                for ext in [
                    ".exe",
                    ".dll",
                    ".so",
                    ".o",
                    ".a",
                    ".dylib",
                    ".class",
                    ".jar",
                    ".war",
                    ".log",
                    ".png",
                    ".jpg",
                    ".jpeg",
                    ".gif",
                    ".svg",
                    ".ico",
                ]
            ):
                continue
            path = os.path.join(root, file)
            if rel_path:
                path = path.replace(repo_path, "")
            all_files.append(path)

    return all_files


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


def read_file_content(file_path):
    def read_file_content(path):
        with open(path, "rb") as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            encoding = result["encoding"]

        with open(path, "r", encoding=encoding) as file:
            content = file.read()
        return content
