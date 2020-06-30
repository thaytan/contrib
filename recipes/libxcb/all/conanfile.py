from conans import *


class LibxcbConan(ConanFile):
    description = "X11 client-side library"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "generators/1.0.0",
        "pkgconf/[^1.6.3]",
        "xcb-proto/[^1.13]",
    )
    requires = (
        "libxau/[^1.0.9]",
        "libpthread-stubs/[^0.4]",
    )

    def source(self):
        tools.get("https://xcb.freedesktop.org/dist/libxcb-%s.tar.bz2" % self.version)

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools.configure(args=args)
            autotools.install()
