from conans import AutoToolsBuildEnvironment, ConanFile, tools


class LibpngConan(ConanFile):
    description = "A collection of routines used to create PNG format graphics files"
    license = "custom"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("autotools/1.0.0@%s/stable" % self.user)

    def requirements(self):
        self.requires("generators/1.0.0@%s/stable" % self.user)
        self.requires("zlib/[>=1.2.11]@%s/stable" % self.user)

    def source(self):
        tools.get("https://downloads.sourceforge.net/sourceforge/libpng/libpng-%s.tar.xz" % self.version)

    def build(self):
        args = ["--disable-static"]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
