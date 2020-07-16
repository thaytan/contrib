from conans import *


class BaseConan(ConanFile):
    name = "base"
    description = "Virtual base package"
    license = "MIT"
    requires = (
        ("generators/[^1.0.0]", "private"),
        "libc/[^1.0.0]",
    )
