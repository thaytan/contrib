from conans import *


class BaseConan(ConanFile):
    name = "base"
    description = "Virtual base package"
    license = "MIT"
    requires = (
        "generators/[^1.0.0]",
        "libc/[^1.0.0]",
    )
