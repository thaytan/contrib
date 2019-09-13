import os
from conans import ConanFile, CMake, tools
from conans.util import files

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "3.3"
    except:
        return None

class GlfwcConan(ConanFile):
    version = get_version()
    name = "glfw"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "GLFW is an Open Source, multi-platform library for OpenGL, OpenGL ES and Vulkan development on the desktop."
    license = "https://github.com/prozum/openhevc/blob/master/LICENSE"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/glfw/glfw/archive/%s.tar.gz" % self.version)

    def build(self):
        cmake = CMake(self)
        cmake.definitions["GLFW_BUILD_EXAMPLES"] = False
        cmake.definitions["GLFW_BUILD_TESTS"] = False
        cmake.definitions["GLFW_BUILD_DOCS"] = False
        cmake.configure(source_dir="%s-%s" % (self.name, self.version))
        cmake.build()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.srcdirs.append("src")
