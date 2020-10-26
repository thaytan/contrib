from build import *


class LibeditRecipe(Recipe):
    description = "System V Release 4.0 curses emulation library"
    license = "Zlib"
    build_requires = ("autotools/[^1.0.0]",)
    requires = ("ncurses/[^6.1]",)

    def source(self):
        self.get(f"https://thrysoee.dk/editline/libedit-{self.version}.tar.gz")
