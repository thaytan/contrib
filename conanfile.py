from conans import CMake, ConanFile, tools


class GTestConan(ConanFile):
    name = "gtest"
    version = tools.get_env("GIT_TAG", "1.8.1")
    description = "Google's C++ test framework"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "BSD-3-Clause"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def build_requirements(self):
        self.build_requires("env-generator/1.0.0@%s/stable" % self.user)
        self.build_requires("cmake/[>=3.15.3]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/google/googletest/archive/release-%s.tar.gz" % self.version)

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.definitions["BUILD_SHARED_LIBS"] = "ON"
        cmake.configure(source_folder="googletest-release-" + self.version)
        cmake.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")
