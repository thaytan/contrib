from build import *


class Glslang(Recipe):
    description = "OpenGL and OpenGL ES shader front end and validator"
    license = "BSD"
    build_requires = (
        "cc/[^1.0.0]",
        "cmake/[^3.18.1]",
    )
    requires = ("python/[^3.8.3]",)

    def source(self):
        self.get(f"https://github.com/KhronosGroup/glslang/archive/{self.version}.tar.gz")