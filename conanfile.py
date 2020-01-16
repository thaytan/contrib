from conans import AutoToolsBuildEnvironment, ConanFile, tools


class LibxcursorConan(ConanFile):
    name = "libxcursor"
    version = tools.get_env("GIT_TAG", "1.2.0")
    description = "X cursor management library"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "custom"
    settings = "os", "compiler", "build_type", "arch"
    generators = "env"

    def build_requirements(self):
        self.build_requires("env-generator/1.0.0@%s/stable" % self.user)
        self.build_requires("autotools/[>=1.0.0]@%s/stable" % self.user)
        self.build_requires("xorg-util-macros/[>=1.19.1]@%s/stable" % self.user)

    def requirements(self):
        self.requires("libxrender/[>=0.9.10]@%s/stable" % self.user)
        self.requires("libxfixes/[>=5.0.3]@%s/stable" % self.user)

    def source(self):
        tools.get("https://xorg.freedesktop.org/releases/individual/lib/libXcursor-%s.tar.gz" % self.version)

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("libXcursor-%s" % self.version):
            autotools.configure(args=args)
            autotools.install()
