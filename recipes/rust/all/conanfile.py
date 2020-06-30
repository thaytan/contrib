import os

from conans import ConanFile, tools
from six import StringIO
import shutil


class RustConan(ConanFile):
    settings = "os", "compiler", "arch"
    license = "MIT", "Apache"
    description = (
        "Systems programming language focused on safety, speed and concurrency"
    )

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("curl/[>=7.66.0]@%s/stable" % self.user)

    def requirements(self):
        self.requires("pkgconf/[>=1.6.3]@%s/stable" % self.user)
        self.requires("clang/[>=9.0.0]@%s/stable" % self.user)
        self.requires("gcc/[>=7.4.0]@%s/stable" % self.user)

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
        arch = {"x86_64": "x86_64", "armv8": "aarch64"}[str(self.settings.arch)]
        src = os.path.join(
            "toolchains", "%s-%s-unknown-linux-gnu" % (self.version, arch)
        )
        self.copy("*", src=os.path.join(src, "bin"), dst="bin")
        self.copy("*.so*", src=os.path.join(src, "lib"), dst="lib")
        self.copy(
            "*",
            src=os.path.join(src, "etc", "bash_completion.d"),
            dst=os.path.join("share", "bash-completion", "completions"),
        )
        self.copy(
            "*",
            src=os.path.join(src, "lib", "rustlib"),
            dst=os.path.join("lib", "rustlib"),
        )

    def package_info(self):
        self.env_info.RUST_SRC_PATH = os.path.join(
            self.package_folder, "lib", "rustlib", "src", "rust", "src"
        )
        git_hash = StringIO()
        if shutil.which("rustc"):
            self.run("rustc -Vv | grep commit-hash | cut -b 14-", output=git_hash)
            self.env_info.SOURCE_MAP.append(
                "/rustc/%s/src|%s"
                % (
                    git_hash.getvalue()[81:-1],
                    os.path.join(
                        self.package_folder, "lib", "rustlib", "src", "rust", "src"
                    ),
                )
            )
