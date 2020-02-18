import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class DirenvConan(ConanFile):
    name = "direnv"
    version = tools.get_env("GIT_TAG", "2.21.2")
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "A shell extension that manages your environment"
    license = "MIT"
    settings = "os", "arch", "compiler"

    def source(self):
        tools.get("https://github.com/direnv/direnv/archive/v{}.tar.gz".format(self.version))

    def build_requirements(self):
        self.build_requires("go/1.13.8@%s/stable" % self.user)

    def requirements(self):
        self.requires("generators/1.0.0@%s/stable" % self.user)

    def build(self):
        env = {"DESTDIR": self.package_folder}
        with tools.chdir("%s-%s" % (self.name, self.version)), tools.environment_append(env):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.make()
            autotools.install()
