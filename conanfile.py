import os

from conans import ConanFile, tools


class RacerConan(ConanFile):
    name = "racer"
    version = tools.get_env("GIT_TAG", "master")
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "Development and debugging tools for GStreamer"
    license = "Apache2"
    settings = "os", "arch", "compiler"
    generators = "env"

    def source(self):
        tools.get("https://github.com/racer-rust/racer/archive/{}.tar.gz".format(self.version))

    def build_requirements(self):
        self.build_requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.build_requires("rust/nightly@%s/stable" % self.user)

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            self.run("cargo build --release")

    def package(self):
        self.copy(pattern="*/racer", dst="bin", keep_path=False)
