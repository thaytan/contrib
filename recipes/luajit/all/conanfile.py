import os

from conans import *


class LuajitConan(ConanFile):
    description = "Just-in-time compiler and drop-in replacement for Lua 5.1"
    license = "MIT"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    build_requires = ("cc/[^1.0.0]",)

    def source(self):
        tools.get(f"https://luajit.org/download/LuaJIT-{self.version}.tar.gz")

    def build(self):
        with tools.chdir(f"LuaJIT-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.make()
            autotools.install(["PREFIX=" + self.package_folder])
