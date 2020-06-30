from conans import ConanFile, tools


class CcConan(ConanFile):
    description = "Virtual C/C++ compiler package"
    license = "GPL"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def requirements(self):
        self.requires("gcc/[^7.4.0]@%s/stable" % self.user)
