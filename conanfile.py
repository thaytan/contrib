import os

from conans import CMake, ConanFile, tools


class RapidJsonConan(ConanFile):
    name = "rapidjson"
    version = tools.get_env("GIT_TAG", "1.1.0")
    license = "MIT"
    description = "A fast JSON parser/generator for C++ with both SAX/DOM style API"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    settings = "os", "compiler", "build_type", "arch"
    generators = "env"

    def build_requirements(self):
        self.build_requires("cmake/[>=3.15.3]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)

    def source(self):
        tools.get(
            "https://github.com/Tencent/rapidjson/archive/v%s.tar.gz" % self.version
        )
        tools.replace_in_file(
            os.path.join("%s-%s" % (self.name, self.version), "CMakeLists.txt"),
            "-Werror",
            "-Wno-implicit-fallthrough",
        )

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.configure(source_folder="%s-%s" % (self.name, self.version))
        cmake.build()
        cmake.install()
