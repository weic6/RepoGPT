import re
import requests
import base64
import os


def crawl_local_repo(repo_path, rel_path=False):
    """
    return paths of all files in a local repository.
    if rel_path is True, return relative paths. Otherwise, return absolute paths.

    """
    all_files = []
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if not d.startswith(".") and not d.startswith("_")]
        for file in files:
            if (
                file.startswith(".")
                or file.startswith("_")
                or file in ["LICENSE", "package-lock.json"]
            ):
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


def get_repo_filetype(repo_path):
    filetypes = set()
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if not d.startswith(".") and not d.startswith("_")]
        for file in files:
            if (
                file.startswith(".")
                or file.startswith("_")
                or file
                in [
                    "LICENSE",
                ]
            ):
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

            _, ext = os.path.splitext(file)
            filetypes.add(ext)
    return filetypes


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


def fetch_file_content(file_path: str):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
    headers = {"Authorization": f"token {github_token}"} if github_token else {}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    # print(response.json())
    content = response.json()["content"]
    return base64.b64decode(content).decode("utf-8")


def read_file_content(file_path: str):
    print(f"Reading file: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
    except UnicodeDecodeError:
        Warning(f"Could not read file {file_path} due to encoding issues.")
    except Exception as e:
        Warning(f"An error occurred while reading the file {file_path}: {e}")
    return content
