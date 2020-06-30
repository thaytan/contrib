import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class LuajitConan(ConanFile):
    description = "Just-in-time compiler and drop-in replacement for Lua 5.1"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("gcc/[^7.4.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://luajit.org/download/LuaJIT-%s.tar.gz" % self.version)

    def build(self):
        with tools.chdir("LuaJIT-%s" % self.version):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.make()
            autotools.install(["PREFIX=%s" % self.package_folder])
