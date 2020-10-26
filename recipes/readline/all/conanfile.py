from build import *


class ReadlineRecipe(Recipe):
    description = "GNU readline library"
    license = "GPL3"
    build_requires = (
        "make/[^4.3]",
        "ncurses/[^6.1]",
    )

    def source(self):
        self.get(f"https://ftp.gnu.org/gnu/readline/readline-{self.version}.tar.gz")

    def build(self):
        args = [
            "--disable-shared",
        ]
        self.autotools(args)
