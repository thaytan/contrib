import util
import os

branch = os.environ["GIT_REF"]
repo = os.environ["CONAN_REPO_REMOVE"]

util.setup_conan([repo])

util.remove_aliases(
    branch,
    repo,
)
