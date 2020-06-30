from conans import CMake, ConanFile, tools


class GlfwcConan(ConanFile):
    name = "glfw"
    description = "GLFW is an Open Source, multi-platform library for OpenGL, OpenGL ES and Vulkan development on the desktop."
    license = "ZLIB"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "x11": [True, False],
    }
    default_options = ("x11=True", )
    exports = "fix-x11-exts.patch"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("cmake/[>=3.15.3]@%s/stable" % self.user)

    def requirements(self):
        if self.options.x11:
            self.requires("libx11/[>=1.6.8]@%s/stable" % self.user)
            self.requires("libxrandr/[>=1.5.2]@%s/stable" % self.user)
            self.requires("libxinerama/[>=1.1.4]@%s/stable" % self.user)
            self.requires("libxcursor/[>=1.2.0]@%s/stable" % self.user)
            self.requires("libxi/[>=1.7.1]@%s/stable" % self.user)

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
