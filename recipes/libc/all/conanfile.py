from build import *


class LibcRecipe(Recipe):
    description = "Virtual libc"
    license = "MIT"

    def requirements(self):
        if self.settings.os_build == "Linux":
            if self.settings.libc_build == "system":
                self.requires("glibc/[~2.27]")
            if self.settings.libc_build == "musl":
                self.requires("musl/[~1.2.1]")
