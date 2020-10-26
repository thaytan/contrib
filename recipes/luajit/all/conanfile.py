from build import *


class LuajitRecipe(Recipe):
    description = "Just-in-time compiler and drop-in replacement for Lua 5.1"
    license = "MIT"
    build_requires = ("make/[^4.3]",)

    def source(self):
        self.get(f"https://luajit.org/download/LuaJIT-{self.version}.tar.gz")

    def build(self):
        args = [
            f"PREFIX={self.package_folder}",
        ]
        self.make(args)
