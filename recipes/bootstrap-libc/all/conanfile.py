from conans import *


class BootstrapLibcConan(ConanFile):
    name = "bootstrap-libc"
    description = "Virtual bootstrap libc package"
    license = "MIT"
    settings = {"os_build": ["Linux"], "libc": ["system", "musl"]}

    def requirements(self):
        if self.settings.os_build == "Linux":
            if self.settings.libc_build == "system":
                self.requires("bootstrap-glibc/[~2.27]")
            if self.settings.libc_build == "musl":
                self.requires("bootstrap-musl/[~1.2.1]")
