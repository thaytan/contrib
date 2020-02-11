import os
import shutil

from conans import ConanFile, tools


class RustupConan(ConanFile):
    name = "rustup"
    version = tools.get_env("GIT_TAG", "1.21.1")
    settings = "os", "compiler", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "MIT", "Apache"
    description = "Systems programming language focused on safety, speed and concurrency"
    generators ="pkgconf"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("rust/[>=1.3.8]@%s/stable" % self.user)

    def requirements(self):
        self.requires("curl/7.66.0@%s/stable" % self.user)
        self.requires("openssl/[>=1.1.1b]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/rust-lang/rustup/archive/{}.tar.gz".format(self.version))

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            self.run("cargo build --release")
            shutil.copyfile(os.path.join("target", "release", "rustup-init"), "rustup")

    def package(self):
        self.copy(pattern="*/rustup", dst="bin", keep_path=False)
