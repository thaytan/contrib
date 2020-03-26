from conans import AutoToolsBuildEnvironment, ConanFile, tools


class LibpngConan(ConanFile):
    name = "libpng"
    version = tools.get_env("GIT_TAG", "1.6.37")
    settings = "os", "compiler", "build_type", "arch"
    license = "custom"
    description = "A collection of routines used to create PNG format graphics files"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)

    def requirements(self):
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
