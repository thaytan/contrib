from conans import AutoToolsBuildEnvironment, ConanFile, tools


class LibxiConan(ConanFile):
    name = "libxi"
    version = tools.get_env("GIT_TAG", "1.7.10")
    description = "X11 Input extension library"
    license = "custom"
    settings = "os", "compiler", "build_type", "arch"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("autotools/[>=1.0.0]@%s/stable" % self.user)
        self.build_requires("xorg-util-macros/[>=1.19.1]@%s/stable" % self.user)

    def requirements(self):
        self.requires("libx11/[>=1.6.8]@%s/stable" % self.user)
        self.requires("libxext/[>=1.3.4]@%s/stable" % self.user)
        self.requires("libxfixes/[>=5.0.3]@%s/stable" % self.user)

    def source(self):
        tools.get("https://xorg.freedesktop.org/releases/individual/lib/libXi-%s.tar.gz" % self.version)

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("libXi-" + self.version):
            autotools.configure(args=args)
            autotools.install()
