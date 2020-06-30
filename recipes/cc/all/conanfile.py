from conans import *


class CcConan(ConanFile):
    description = "Virtual C/C++ compiler package"
    license = "GPL"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    )
    requires = (
        "gcc/[^7.4.0]",
