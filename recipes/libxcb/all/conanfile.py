from conans import AutoToolsBuildEnvironment, ConanFile, tools


class LibxcbConan(ConanFile):
    name = "libxcb"
    description = "X11 client-side library"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("pkgconf/[>=1.6.3]@%s/stable" % self.user)
        self.build_requires("xcb-proto/[>=1.13]@%s/stable" % self.user)

    def requirements(self):
        self.requires("libxau/[>=1.0.9]@%s/stable" % self.user)
        self.requires("libpthread-stubs/[>=0.4]@%s/stable" % self.user)

    def source(self):
        tools.get("https://xcb.freedesktop.org/dist/libxcb-%s.tar.bz2" % self.version)

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools.configure(args=args)
            autotools.install()
