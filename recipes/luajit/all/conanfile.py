import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class LuajitConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    license = "MIT"
    description = "Just-in-time compiler and drop-in replacement for Lua 5.1"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("gcc/[>=7.4.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://luajit.org/download/LuaJIT-%s.tar.gz" % self.version)

    def build(self):
        with tools.chdir("LuaJIT-%s" % self.version):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.make()
            autotools.install(["PREFIX=%s" % self.package_folder])
