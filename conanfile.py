import os

from conans import ConanFile, tools


class NinjaConan(ConanFile):
    name = "ninja"
    version = tools.get_env("GIT_TAG", "1.9.0")
    license = "Apache"
    description = "Small build system with a focus on speed"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    settings = "os", "compiler", "build_type", "arch"
    generators ="pkgconf"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("gcc/[>=7.4.0]@%s/stable" % self.user)
        self.build_requires("python/[>=3.7.4]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/ninja-build/ninja/archive/v%s.tar.gz" % self.version)

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            self.run("python configure.py --bootstrap")

    def package(self):
        self.copy(
            os.path.join("%s-%s" % (self.name, self.version), "ninja"),
            "bin",
            keep_path=False,
        )
