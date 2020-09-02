from conans import *


class BootstrapLibcConan(ConanFile):
    name = "bootstrap-libc"
    description = "Virtual bootstrap libc package"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"

    def requirements(self):
        if self.settings.os_build == "Linux":
            if self.settings.libc_build == "system":
                self.requires("bootstrap-glibc-headers/[~2.27]")
            if self.settings.libc_build == "musl":
                self.requires("bootstrap-musl-headers/[~1.2.1]")
