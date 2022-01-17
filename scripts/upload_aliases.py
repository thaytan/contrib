import util
import os
import subprocess

branch = os.environ["CI_COMMIT_REF_NAME"]
process = subprocess.Popen(["git", "show-ref", branch, "--heads", "--tag", "-s"], stdout=subprocess.PIPE)
commit = process.communicate()[0].strip()

print(f"Branch: {branch}")
old_branch = os.environ["CI_MERGE_REQUEST_TARGET_BRANCH_NAME"]
print(f"Target Branch: {old_branch}")
fetch_repo = os.environ["CONAN_REPO_ALL"]
print(f"Fetching from: {fetch_repo}")
public_repo = os.environ["CONAN_REPO_PUBLIC"]
print(f"Uploading public to: {public_repo}")
internal_repo = os.environ["CONAN_REPO_INTERNAL"]
print(f"Uploading internal to: {internal_repo}")

util.setup_conan((fetch_repo, [public_repo, internal_repo]))

util.create_aliases(
    commit,
    branch,
    old_branch,
    fetch_repo,
    public_repo,
    internal_repo,
)
