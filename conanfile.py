import os

from conans import ConanFile, tools


class GoConan(ConanFile):
    name = "go"
    version = tools.get_env("GIT_TAG", "1.13.8")
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "BSD"
    description = "Core compiler tools for the Go programming language"
    settings = "os", "compiler", "arch"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)

    def source(self):
        arch = {"x86_64": "amd64", "armv8": "arm64"}[str(self.settings.arch)]
        tools.get("https://dl.google.com/go/go{}.linux-{}.tar.gz".format(self.version, arch))

    def package(self):
        self.copy("*bin/go*")
