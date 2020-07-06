from conans import *


class LibcxxConan(ConanFile):
    description = "Virtual libc++ package"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"], "libcxx": ["system", "libc++"]}
    license = "Public"

    def requirements(self):
        if self.settings.libcxx == "libc++":
            self.requires("libc++/[^10.0.0]")
