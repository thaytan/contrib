import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools


class OpusConan(ConanFile):
    name = "opus"
    version = "1.3.1"
    license = "https://raw.githubusercontent.com/xiph/opus/master/COPYING"
    description = "Modern audio compression for the internet"
    url = "https://gitlab.com/aivero/public/conan/conan-librealsense"
    settings = "os", "compiler", "build_type", "arch"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/%s" % (self.user, self.channel))

    def source(self):
        tools.get("https://archive.mozilla.org/pub/opus/opus-%s.tar.gz" % self.version)

    def build(self):
        with tools.chdir("opus-" + self.version):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.make(args=["install"])

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.cpp", "src")
            self.copy("*.hpp", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.libs = ["opus"]
        self.cpp_info.srcdirs.append("src")
