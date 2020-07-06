from conans import *


class LibcConan(ConanFile):
    name = "libc"
    description = "Virtual libc package"
    license = "MIT"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"], "libc": ["glibc", "musl", "system"]}

    def requirements(self):
        if self.settings.libc == "glibc":
            self.requires("glibc/[^2.27]")
        if self.settings.libc == "musl":
            self.requires("musl/[^1.2.0]")
