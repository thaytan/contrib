import os

from conans import ConanFile, tools


class RustfmtConan(ConanFile):
    description = "A tool for formatting Rust code according to style guidelines"
    license = "MIT"
    settings = "os", "arch", "compiler"

    def source(self):
        tools.get(
            "https://github.com/rust-lang/rustfmt/archive/{}.tar.gz".format(
                self.version
            )
        )

    def requirements(self):
        self.requires("rust/nightly@%s/stable" % self.user)
        self.requires("generators/[>=1.0.0]@%s/stable" % self.user)

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            self.run("cargo build --release")

    def package(self):
        self.copy(pattern="*/rustfmt", dst="bin", keep_path=False)
