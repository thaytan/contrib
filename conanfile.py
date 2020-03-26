import os

from conans import ConanFile, tools


class GoConan(ConanFile):
    name = "go"
    version = tools.get_env("GIT_TAG", "1.13.8")
    license = "BSD"
    description = "Core compiler tools for the Go programming language"
    settings = "os", "compiler", "arch"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)

    def source(self):
        arch = {"x86_64": "amd64", "armv8": "arm64"}[str(self.settings.arch)]
        filename = "go{}.linux-{}.tar.gz".format(self.version, arch)
        tools.download("https://dl.google.com/go/go{}.linux-{}.tar.gz".format(self.version, arch), filename)
        # Workaround: Python3 in Ubuntu 18.04 does not support ascii encoded tarballs
        self.run("tar -xf " + filename)

    def package(self):
        self.copy("*", src="go/bin", dst="bin")
        self.copy("*", src="go/src", dst="src")
        self.copy("*", src="go/pkg", dst="pkg")

    def package_info(self):
        self.env_info.GOROOT = self.package_folder
