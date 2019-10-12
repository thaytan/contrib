import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class PerlConan(ConanFile):
    name = "perl"
    version = tools.get_env("GIT_TAG", "5.30.0")
    settings = "os", "compiler", "build_type", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "GPL"
    description = "A highly capable, feature-rich programming language"
    generators = "env"

    def build_requirements(self):
        self.build_requires("gcc/[>=7.4.0]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/Perl/perl5/archive/v%s.tar.gz" % self.version)

    def build(self):
        args = [
            "-des",
            "-Dusethreads",
            "-Duseshrplib",
            "-Dprefix=" + self.package_folder,
        ]
        with tools.chdir("%s5-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            self.run("./Configure " + " ".join(args))
            autotools.make()
            autotools.install()
