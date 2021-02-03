import util
import os

branch = os.environ["GITHUB_REF"].split("/")[2]
repo = os.environ["CONAN_REPO_REMOVE"]

util.remove_aliases(
    branch,
    repo,
)
