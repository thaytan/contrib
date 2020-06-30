import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class M4Conan(ConanFile):
    description = "The GNU macro processor"
    license = "GPL3"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("bootstrap-gcc/[^7.4.0]@%s/stable" % self.user)
        self.build_requires("make/[^4.3]@%s/stable" % self.user)

    def source(self):
        tools.get("https://ftp.gnu.org/gnu/m4/m4-%s.tar.gz" % self.version)

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.make(target="install-strip")

    def package_info(self):
        self.env_info.M4 = os.path.join(self.package_folder, "bin", "m4")
