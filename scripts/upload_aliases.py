import util
import os
import subprocess

branch = os.environ["CI_COMMIT_REF_NAME"]
process = subprocess.Popen(["git", "show-ref", branch, "--heads", "--tag", "-s"], stdout=subprocess.PIPE)
commit = process.communicate()[0].strip()

print(f"Branch: {branch}")
old_branch = "master"
fetch_repo = os.environ["CONAN_REPO_ALL"]
print(f"Fetching from: {fetch_repo}")
upload_repo = os.environ["CONAN_REPO_UPLOAD"]
print(f"Uploading to: {upload_repo}")

util.setup_conan((fetch_repo, upload_repo))

util.create_aliases(
    commit,
    branch,
    old_branch,
    fetch_repo,
    upload_repo,
)
