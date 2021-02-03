import util
import os

branch = os.environ["GITHUB_REF"].split("/")[2]
old_branch = "master"
upload_repo = os.environ["CONAN_REPO_UPLOAD"]

util.create_aliases(
    branch,
    old_branch,
    upload_repo,
)
