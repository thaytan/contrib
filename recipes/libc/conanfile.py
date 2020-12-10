from build import *


class LibcRecipe(Recipe):
    description = "Virtual libc"
    license = "MIT"
    options = {}
    default_options = {}

    def requirements(self):
        if self.settings.libc == "glibc":
            self.requires("glibc/[~2.27]")
        if self.settings.libc == "musl":
            self.requires("musl/[~1.2.1]")
        if self.settings.libc == "bionic":
            self.requires("bionic/[~28]")
