from conans import ConanFile, tools


class CcConan(ConanFile):
    settings = "os", "compiler", "arch"
    license = "GPL"
    description = "Virtual C/C++ compiler package"

    def requirements(self):
        self.requires("gcc/[>=7.4.0]@%s/stable" % self.user)
