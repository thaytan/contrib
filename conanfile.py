from conans import ConanFile, tools


class BootstrapMakeConan(ConanFile):
    name = "bootstrap-gcc"
    version = tools.get_env("GIT_TAG", "4.3")
    settings = "os", "compiler", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "custom", "FDL", "GPL", "LGPL"
    description = "The GNU Compiler Collection - C and C++ frontends"

    def package_info(self):
        self.env_info.MAKE = "/usr/bin/make"
