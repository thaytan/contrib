from conans import AutoToolsBuildEnvironment, ConanFile, tools


class LibxfixesConan(ConanFile):
    name = "libxfixes"
    version = tools.get_env("GIT_TAG", "5.0.3")
    description = "X11 miscellaneous 'fixes' extension library"
    license = "custom"
    settings = "os", "compiler", "build_type", "arch"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("pkgconf/[>=1.6.3]@%s/stable" % self.user)
        self.build_requires("xorg-util-macros/[>=1.19.1]@%s/stable" % self.user)

    def requirements(self):
        self.requires("libx11/[>=1.6.8]@%s/stable" % self.user)

    def source(self):
        tools.get("https://xorg.freedesktop.org/releases/individual/lib/libXfixes-%s.tar.gz" % self.version)

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("libXfixes-" + self.version):
            autotools.configure(args=args)
            autotools.install()
