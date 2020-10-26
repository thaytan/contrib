from conans import *


class LuajitConan(ConanFile):
    description = "Just-in-time compiler and drop-in replacement for Lua 5.1"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("make/[^4.3]",)

    def source(self):
        tools.get(f"https://luajit.org/download/LuaJIT-{self.version}.tar.gz")

    def build(self):
        with tools.chdir(f"LuaJIT-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.make()
            autotools.install([f"PREFIX={self.package_folder}"])
