from conans import *


class BaseConan(ConanFile):
    name = "base"
    description = "Virtual base package"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"], "libc": ["glibc", "musl", "system"]}
    license = "Public"

    def requirements(self):
        self.requires("generators/[^1.0.0]")
        self.requires("base/[^1.0.0]")
