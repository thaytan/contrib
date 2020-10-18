import os
import shutil

from conans import *


class RustupConan(ConanFile):
    description = "Systems programming language focused on safety, speed and concurrency"
    license = "MIT", "Apache"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("rust/[^1.3.8]",)
    requires = (
        "base/[^1.0.0]",
        "curl/7.66.0",
        "openssl/[^1.1.1b]",
    )

    def source(self):
        tools.get(f"https://github.com/rust-lang/rustup/archive/{self.version}.tar.gz")

    def build(self):
        with tools.chdir(f"{self.name}-{self.version}"):
            self.run('cargo build --release --features "no-self-update" --bin rustup-init')
            shutil.copy2(os.path.join("target", "release", "rustup-init"), "rustup")

    def package(self):
        self.copy(pattern="*/rustup", dst="bin", keep_path=False)
        bins = [
            "cargo",
            "rustc",
            "rustdoc",
            "rust-gdb",
            "rust-lldb",
            "rls",
            "rustfmt",
            "cargo-fmt",
            "cargo-clippy",
            "clippy-driver",
            "cargo-miri",
        ]
        for bin in bins:
            os.symlink("rustup", os.path.join(self.package_folder, "bin", bin))
