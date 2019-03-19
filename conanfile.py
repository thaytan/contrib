import os
from conans import ConanFile, CMake, tools
from conans.util import files


class CppzmqConan(ConanFile):
    name = "cppzmq"
    version = "4.3.0"
    license = "https://raw.githubusercontent.com/zeromq/cppzmq/master/COPYING"
    description = "ZeroMQ core engine in C++, implements ZMTP/3.1"
    default_user = "bincrafters"
    default_channel = "stable"
    url = "https://github.com/bincrafters/conan-" + name
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"

    def requirements(self):
        self.requires("libzmq/4.3.1@%s/%s" % (self.user, self.channel))

    def source(self):
        tools.get("https://github.com/zeromq/cppzmq/archive/v%s.tar.gz" % self.version)

    def build(self):
        cmake = CMake(self)
        vars = {
            "CFLAGS": "-fdebug-prefix-map=%s=." % self.source_folder,
            "CXXFLAGS": "-fdebug-prefix-map=%s=." % self.source_folder,
        }
        with tools.environment_append(vars):
            cmake.configure(source_folder=self.name + "-" + self.version)
            cmake.build()
            cmake.install()

    def package(self):
        if self.channel == "testing":
            self.copy("*.cpp", "src")
            self.copy("*.hpp", "src")

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.SOURCE_PATH.append(os.path.join(self.package_folder, "src"))
        self.cpp_info.srcdirs.append("src")
