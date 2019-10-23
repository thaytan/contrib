import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class Bzip2Conan(ConanFile):
    name = "bzip2"
    version = tools.get_env("GIT_TAG", "1.0.8")
    url = "https://gitlab.com/aivero/public/conan/conan-bison"
    description = "A high-quality data compression program"
    license = "custom"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def build_requirements(self):
        self.build_requires("gcc/[>=7.4.0]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://sourceware.org/pub/bzip2/bzip2-%s.tar.gz" % self.version)

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            self.run("make -f Makefile-libbz2_so")
            autotools.make(target="bzip2")
            autotools.install(args=["PREFIX=" + self.package_folder])

    def package(self):
        self.copy(pattern="*libbz2.so*", dst="lib", symlinks=True, keep_path=False)
        os.symlink(
            "libbz2.so.%s" % self.version,
            os.path.join(self.package_folder, "lib", "libbz2.so"),
        )
