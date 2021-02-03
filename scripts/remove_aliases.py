import util
import os

branch = os.environ["GIT_REF"]
print(f"Branch: {branch}")
repo = os.environ["CONAN_REPO_REMOVE"]
print(f"Removing from: {upload_repo}")

util.setup_conan([repo])

util.remove_aliases(
    branch,
    repo,
)
