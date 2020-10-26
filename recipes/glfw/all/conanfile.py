from build import *


class GlfwcRecipe(Recipe):
    description = "GLFW is an Open Source, multi-platform library for OpenGL, OpenGL ES and Vulkan development on the desktop."
    license = "ZLIB"
    options = {"x11": [True, False]}
    default_options = ("x11=True",)
    exports = "fix-x11-exts.patch"
    build_requires = ("cmake/[^3.15.3]",)

    def requirements(self):
        if self.options.x11:
            self.requires("libx11/[^1.6.8]")
            self.requires("libxrandr/[^1.5.2]")
            self.requires("libxinerama/[^1.1.4]")
            self.requires("libxcursor/[^1.2.0]")
            self.requires("libxi/[^1.7.1]")

    def source(self):
        self.get(f"https://github.com/glfw/glfw/archive/{self.version}.tar.gz")
        self.patch("fix-x11-exts.patch")

    def build(self):
        defs = {
            "BUILD_SHARED_LIBS": True,
            "GLFW_BUILD_EXAMPLES": False,
            "GLFW_BUILD_TESTS": False,
            "GLFW_BUILD_DOCS": False,
        }
        self.cmake(defs)
