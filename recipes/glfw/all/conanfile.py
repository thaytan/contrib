from conans import *


class GlfwcConan(ConanFile):
    description = "GLFW is an Open Source, multi-platform library for OpenGL, OpenGL ES and Vulkan development on the desktop."
    license = "ZLIB"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    options = {"x11": [True, False]}
    default_options = ("x11=True",)
    exports = "fix-x11-exts.patch"
    build_requires = (
        "generators/1.0.0",
        "cmake/[^3.15.3]",
    )
    requires = (
        if self.options.x11:
            "libx11/[^1.6.8]",
            "libxrandr/[^1.5.2]",
            "libxinerama/[^1.1.4]",
            "libxcursor/[^1.2.0]",
            "libxi/[^1.7.1]",
    )

    def source(self):
        tools.get("https://github.com/glfw/glfw/archive/%s.tar.gz" % self.version)
        tools.patch(patch_file="fix-x11-exts.patch", base_path="%s-%s" % (self.name, self.version))

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.definitions["BUILD_SHARED_LIBS"] = True
        cmake.definitions["GLFW_BUILD_EXAMPLES"] = False
        cmake.definitions["GLFW_BUILD_TESTS"] = False
        cmake.definitions["GLFW_BUILD_DOCS"] = False
        cmake.configure(source_dir="%s-%s" % (self.name, self.version))
        cmake.build()
        cmake.install()
