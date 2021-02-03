import util
import os

branch = os.environ["GITHUB_REF"].split("/")[2]
print(f"Branch: {branch}")
old_branch = "master"
fetch_repo = os.environ["CONAN_REPO_ALL"]
print(f"Fetching from: {fetch_repo}")
upload_repo = os.environ["CONAN_REPO_UPLOAD"]
print(f"Uploading to: {upload_repo}")

util.create_aliases(
    branch,
    old_branch,
    fetch_repo,
    upload_repo,
)
