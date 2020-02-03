from conans import ConanFile, tools


class CcConan(ConanFile):
    name = "cc"
    version = tools.get_env("GIT_TAG", "1.0.0")
    settings = "os", "compiler", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "GPL"
    description = "Virtual C/C++ compiler package"

    def requirements(self):
        self.requires("gcc/[>=7.4.0]@%s/stable" % self.user)
