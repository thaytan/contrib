from build import *


class LuajitRecipe(Recipe):
    description = "Just-in-time compiler and drop-in replacement for Lua 5.1"
    license = "MIT"
    build_requires = (
        "cc/[^1.0.0]",
        "make/[^4.3]",
    )

    def source(self):
        self.get(f"https://luajit.org/download/LuaJIT-{self.version}.tar.gz")

    def build(self):
        args = [
            f"PREFIX={self.package_folder}",
            f"DEFAULT_CC={self.env['CC']}",
        ]
        self.make(args)
