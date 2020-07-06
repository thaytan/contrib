from conans import *


class CcConan(ConanFile):
    name = "cc"
    description = "Virtual C/C++ compiler package"
    license = "GPL"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    )
    requires = (
        "cc/[^1.0.0]",
