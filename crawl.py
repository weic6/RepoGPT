import re
import requests
import base64
import os
import fnmatch


patterns_excluded = [
    "LICENSE",
    ".*",  # files starting with a dot
    "_*",  # files starting with an underscore
    "*.exe",
    "*.dll",
    "*.so",
    "*.o",
    "*.a",
    "*.dylib",
    "*.class",
    "*.jar",
    "*.war",
    "*.zip",
    "*.log",
    "*.png",
    "*.jpg",
    "*.jpeg",
    "*.gif",
    "*.svg",
    "*.ico",
]


def is_excluded(name):
    return any(fnmatch.fnmatch(name, pattern) for pattern in patterns_excluded)


def crawl_local_repo(repo_path, rel_path=False):
    """
    return absolute paths of all files in a local repository.
    if rel_path is True, return relative paths.

    """
    all_files = []
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if not is_excluded(d)]
        for file in files:
            if is_excluded(file):
                continue
            path = os.path.join(root, file)
            if rel_path:
                path = path.replace(repo_path, "")
            all_files.append(path)
    return all_files


def get_repo_filetype(repo_path):
    filetypes = set()
    files = crawl_local_repo(repo_path)
    for file in files:
        _, ext = os.path.splitext(file)
        filetypes.add(ext)
    return filetypes


def git_extract_owner_repo(url):
    pattern = r"github\.com/([^/]+)/([^/]+)"
    match = re.search(pattern, url)
    if match:
        owner, repo = match.groups()
        repo = repo.split("/")[0]
        # print(f"Owner: {owner}, Repo: {repo}")
        return owner, repo
    return None, None


def git_get_repo_contents(owner, repo, path="", github_token=None):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {"Authorization": f"token {github_token}"} if github_token else {}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def git_crawl_repo(owner, repo, github_token=None):
    all_files = []

    def crawl_path(path):
        contents = git_get_file_content(owner, repo, path, github_token)
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


def git_get_file_content(owner, repo, path, github_token)
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {"Authorization": f"token {github_token}"} if github_token else {}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    # print(response.json())
    content = response.json()["content"]
    return base64.b64decode(content).decode("utf-8")




