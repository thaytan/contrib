import util
import os

branch = os.environ["CI_COMMIT_REF_NAME"]
print(f"Branch: {branch}")
public_repo = os.environ["CONAN_REPO_PUBLIC"]
print(f"Removing public from: {public_repo}")
internal_repo = os.environ["CONAN_REPO_INTERNAL"]
print(f"Removing internal from: {internal_repo}")

util.setup_conan([repo])

util.remove_aliases(
    branch,
    public_repo,
    internal_repo
)
