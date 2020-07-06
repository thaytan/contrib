from conans import *


class LibcConan(ConanFile):
    description = "Virtual libc package"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"], "libc": ["glibc", "musl", "system"]}

    def requirements(self):
        if self.settings.libc == "glibc":
            self.requires("glibc/[^2.27]")
        if self.settings.libc == "musl":
            self.requires("musl/[^1.2.0]")
