from conans import ConanFile, tools


class AutotoolsConan(ConanFile):
    description = "A suite of programming tools 'designed' to assist in making source code"
    license = "GPL"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def requirements(self):
        self.requires("cc/[^1.0.0]")
        self.requires("make/[^3.4.0]")
        self.requires("autoconf/[^2.69]")
        self.requires("automake/[^1.16.1]")
        self.requires("libtool/[^2.4.6]")
        self.requires("pkgconf/[^1.6.3]")
        self.requires("gettext/[^0.20.1]")
        self.requires("texinfo/[^6.6]")
