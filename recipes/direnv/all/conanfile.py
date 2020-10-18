import os
from conans import *


class DirenvConan(ConanFile):
    description = "A shell extension that manages your environment"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "go/[^1.15.3]",
        "make/[^4.3]",
        "clang/[^10.0.1]",
    )

    def source(self):
        tools.get(f"https://github.com/direnv/direnv/archive/v{self.version}.tar.gz")

    def build(self):
        env = {
            "GOFLAGS": "-buildmode=pie -trimpath -mod=vendor -modcacherw",
            "DESTDIR": self.package_folder,
        }
        with tools.chdir(f"direnv-{self.version}"), tools.environment_append(env):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.make()
            autotools.install()
