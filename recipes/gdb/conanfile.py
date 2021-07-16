from build import *


class GdbRecipe(Recipe):
    description = "The GNU Debugger"
    license = "GPL"
    build_requires = ("texinfo/[^6.6]",)
    requires = (
        "ncurses/[^6.1]",
        "readline/[^8.0]",
    )

    def requirements(self):
        self.requires(f"python/[^3]")

    def source(self):
        self.get(f"https://ftp.gnu.org/gnu/gdb/gdb-{self.version}.tar.gz")

    def build(self):
        args = [
            "--enable-tui=yes",
            "--with-system-readline",
        ]
        self.autotools(args)

    def package_info(self):
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "share", "gdb", "python"))
