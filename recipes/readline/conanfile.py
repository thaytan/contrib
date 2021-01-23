from build import *


class ReadlineRecipe(Recipe):
    description = "GNU readline library"
    license = "GPL"
    build_requires = (
        "cc/[^1.0.0]",
        "make/[^4.3]",
    )
    requires = ("ncurses/[^6.1]",)

    def source(self):
        self.get(f"https://ftp.gnu.org/gnu/readline/readline-{self.version}.tar.gz")
