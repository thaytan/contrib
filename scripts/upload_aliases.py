import util
import os
import subprocess

branch = os.environ["CI_COMMIT_REF_NAME"]
process = subprocess.Popen(["git", "show-ref", branch, "--heads", "--tag", "-s"], stdout=subprocess.PIPE)
commit = process.communicate()[0].strip()

print(f"Branch: {branch}")
parent_branch = util.find_parent_branch()
print(f"Parent Branch: {parent_branch}")
fetch_repo = os.environ["CONAN_REPO_ALL"]
print(f"Fetching from: {fetch_repo}")
public_repo = os.environ["CONAN_REPO_PUBLIC"]
print(f"Uploading public to: {public_repo}")
internal_repo = os.environ["CONAN_REPO_INTERNAL"]
print(f"Uploading internal to: {internal_repo}")

util.setup_conan((fetch_repo, public_repo, internal_repo))

util.create_aliases(
    commit,
    branch,
    parent_branch,
    fetch_repo,
    public_repo,
    internal_repo,
)
