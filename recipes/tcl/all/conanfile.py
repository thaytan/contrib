from build import *


class TclRecipe(Recipe):
    description = "The Tcl scripting language"
    license = "custom"
    build_requires = (
        "make/[^4.3]",
        "zlib/[^1.2.11]",
    )

    def source(self):
        self.get(f"https://downloads.sourceforge.net/sourceforge/tcl/tcl{self.version}-src.tar.gz")

    def build(self):
        args = [
            "--enable-threads",
            "--enable-64bit",
        ]
        os.environ["CFLAGS"] += " -lm"
        self.autotools(args)
