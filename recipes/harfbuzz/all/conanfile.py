from glob import glob
from os import path, remove

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class HarfbuzzConan(ConanFile):
    description = "HarfBuzz text shaping engine"
    license = "Old MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("autotools/[>=1.0.0]@%s/stable" % self.user)
        self.build_requires("freetype-no-harfbuzz/[>=2.10.1]@%s/stable" % self.user)

    def requirements(self):
        self.requires("glib/[>=2.62.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/harfbuzz/harfbuzz/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--disable-static"]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.install()
