from conans import *


class LibxcbConan(ConanFile):
    description = "X11 client-side library"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0")
        self.build_requires("pkgconf/[^1.6.3]")
        self.build_requires("xcb-proto/[^1.13]")

    def requirements(self):
        self.requires("libxau/[^1.0.9]")
        self.requires("libpthread-stubs/[^0.4]")

    def source(self):
        tools.get("https://xcb.freedesktop.org/dist/libxcb-%s.tar.bz2" % self.version)

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools.configure(args=args)
            autotools.install()
