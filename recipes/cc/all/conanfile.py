from conans import *


class CCConan(ConanFile):
    description = "Virtual c/c++ compiler package"
    license = "GPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    requires = ("clang/[^10.0.1]",)
