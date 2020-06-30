import os
import shutil

from conans import ConanFile, tools


class RustupConan(ConanFile):
    description = "Systems programming language focused on safety, speed and concurrency"
    license = "MIT", "Apache"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0")
        self.build_requires("rust/[^1.3.8]")

    def requirements(self):
        self.requires("curl/7.66.0")
        self.requires("openssl/[^1.1.1b]")

    def source(self):
        tools.get("https://github.com/rust-lang/rustup/archive/{}.tar.gz".format(self.version))

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
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
