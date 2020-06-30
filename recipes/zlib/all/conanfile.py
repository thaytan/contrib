from conans import AutoToolsBuildEnvironment, ConanFile, tools


class ZlibConan(ConanFile):
    license = "Zlib"
    description = (
        "A Massively Spiffy Yet Delicately Unobtrusive Compression Library "
        "(Also Free, Not to Mention Unencumbered by Patents)"
    )
    settings = "os", "arch", "compiler", "build_type"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("autotools/[>=1.0.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/madler/zlib/archive/v%s.tar.gz" % self.version)

    def build(self):
        args = ["--enable-shared"]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
