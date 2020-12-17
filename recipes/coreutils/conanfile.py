from build import *


class CoreutilsRecipe(Recipe):
    description = "The basic file, shell and text manipulation utilities of the GNU operating system"
    license = "GPL3"

    def source(self):
        self.get(f"https://ftp.gnu.org/gnu/coreutils/coreutils-{self.version}.tar.xz")