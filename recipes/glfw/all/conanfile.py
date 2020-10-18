from conans import *


class GlfwcConan(ConanFile):
    description = "GLFW is an Open Source, multi-platform library for OpenGL, OpenGL ES and Vulkan development on the desktop."
    license = "ZLIB"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
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
        tools.get(f"https://github.com/glfw/glfw/archive/{self.version}.tar.gz")
        tools.patch(patch_file="fix-x11-exts.patch", base_path=f"{self.name}-{self.version}")

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.definitions["BUILD_SHARED_LIBS"] = True
        cmake.definitions["GLFW_BUILD_EXAMPLES"] = False
        cmake.definitions["GLFW_BUILD_TESTS"] = False
        cmake.definitions["GLFW_BUILD_DOCS"] = False
        cmake.configure(source_dir=f"{self.name}-{self.version}")
        cmake.build()
        cmake.install()
