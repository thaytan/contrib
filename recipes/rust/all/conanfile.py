import os

from conans import *
from six import StringIO
import shutil


class RustConan(ConanFile):
    description = "Systems programming language focused on safety, speed and concurrency"
    license = "MIT", "Apache"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    build_requires = (
        "curl/[^7.66.0]",
    )
    requires = (
        "base/[^1.0.0]",
        "pkgconf/[^1.6.3]",
        "clang/[^9.0.0]",
        "cc/[^1.0.0]",
    )

    def source(self):
        tools.download("https://sh.rustup.rs", "rustup.sh")

    def build(self):
        env = {
            "HOME": self.build_folder,  # To avoid rustup writing to $HOME/.profile
            "RUSTUP_HOME": self.build_folder,
            "CARGO_HOME": self.build_folder,
        }
        with tools.environment_append(env):
            self.run("sh rustup.sh -y --default-toolchain " + self.version)
            self.run("./bin/rustup component add rust-src rustc-dev")

    def package(self):
        arch = {"x86_64": "x86_64", "armv8": "aarch64"}[str(self.settings.arch_build)]
        src = os.path.join(f"toolchains", "{self.version}-{arch}-unknown-linux-gnu")
        self.copy("*", src=os.path.join(src, "bin"), dst="bin")
        self.copy("*.so*", src=os.path.join(src, "lib"), dst="lib")
        self.copy(
            "*", src=os.path.join(src, "etc", "bash_completion.d"), dst=os.path.join("share", "bash-completion", "completions")\        )
        self.copy(
            "*", src=os.path.join(src, "lib", "rustlib"), dst=os.path.join("lib", "rustlib")\        )

    def package_info(self):
        self.env_info.RUST_SRC_PATH = os.path.join(self.package_folder, "lib", "rustlib", "src", "rust", "src")
        git_hash = StringIO()
        if shutil.which("rustc"):
            self.run("rustc -Vv | grep commit-hash | cut -b 14-", output=git_hash)
            git_hash = git_hash.getvalue()[81:-1]
            path = os.path.join(self.package_folder, "lib", "rustlib", "src", "rust", "src")
            self.env_info.SOURCE_MAP.append(f"/rustc/${git_hash}/src|{path}"
