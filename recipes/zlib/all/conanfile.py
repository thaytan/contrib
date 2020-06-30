from conans import *


class ZlibConan(ConanFile):
    description = "A Massively Spiffy Yet Delicately Unobtrusive Compression Library " "(Also Free, Not to Mention Unencumbered by Patents)"
    license = "Zlib"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "generators/1.0.0",
        "autotools/[^1.0.0]",
    )

    def source(self):
        tools.get("https://github.com/madler/zlib/archive/v%s.tar.gz" % self.version)

    def build(self):
        args = ["--enable-shared"]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
