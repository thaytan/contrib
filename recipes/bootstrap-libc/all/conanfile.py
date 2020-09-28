from conans import *


class BootstrapLibcConan(ConanFile):
    description = "Virtual bootstrap libc"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"

    def requirements(self):
        if self.settings.os_build == "Linux":
            if self.settings.libc_build == "system":
                self.requires("bootstrap-glibc-headers-dev/[~2.27]")
            if self.settings.libc_build == "musl":
                self.requires("bootstrap-musl-dev/[~1.2.1]")
