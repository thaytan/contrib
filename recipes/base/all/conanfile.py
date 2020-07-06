from conans import *


class BaseConan(ConanFile):
    description = "Virtual base package"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"], "libc": ["glibc", "musl", "system"]}
    license = "Public"

    def requirements(self):
        self.requires("generators/[^1.0.0]")
        self.requires("base/[^1.0.0]")
