import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class NpmConan(ConanFile):
    name = "npm"
    version = tools.get_env("GIT_TAG", "6.14.5")
    description = "Evented I/O for V8 javascript"
    license = "MIT"
    settings = "os", "arch", "compiler"

    def build_requirements(self):
        self.build_requires("python/[>=3.7.4]@%s/stable" % self.user)

    def requirements(self):
        self.requires("generators/1.0.0@%s/stable" % self.user)
        self.requires("nodejs/[>=13.0.1]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/npm/cli/archive/v%s.tar.gz" % self.version)

    def build(self):
        with tools.chdir("cli-%s" % self.version):
            autotools = AutoToolsBuildEnvironment(self)
            self.run("mkdir -p man/man1")
            autotools.install(['NPMOPTS=--prefix="%s"' % self.package_folder])
