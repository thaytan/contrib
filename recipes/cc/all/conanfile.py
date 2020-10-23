from conans import *


class CCConan(ConanFile):
    description = "Virtual c/c++ compiler package"
    license = "GPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    requires = ("llvm/[^11.0.0]",)
