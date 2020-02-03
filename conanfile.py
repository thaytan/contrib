from conans import ConanFile, tools


class GccConan(ConanFile):
    name = "bootstrap-gcc"
    version = tools.get_env("GIT_TAG", "7.4.0")
    settings = "os", "compiler", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "custom", "FDL", "GPL", "LGPL"
    description = "The GNU Compiler Collection - C and C++ frontends"

    def package_info(self):
        self.env_info.CC = "/usr/bin/gcc-7"
        self.env_info.CXX = "/usr/bin/g++-7"
