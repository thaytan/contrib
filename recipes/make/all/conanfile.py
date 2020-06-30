import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class MakeConan(ConanFile):
    name = "make"
    settings = "os", "compiler", "arch"
    license = "GPL"
    description = "GNU make utility to maintain groups of programs"

    def build_requirements(self):
        self.build_requires("bootstrap-gcc/7.4.0@%s/stable" % self.user)
        self.build_requires("bootstrap-make/4.3@%s/stable" % self.user)

    def source(self):
        tools.get("https://ftp.gnu.org/gnu/make/make-{}.tar.gz".format(self.version))

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.install()

    def package_info(self):
        self.env_info.MAKE = os.path.join(self.package_folder, "bin", "make")
