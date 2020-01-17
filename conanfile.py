from conans import AutoToolsBuildEnvironment, ConanFile, tools


class LibxauConan(ConanFile):
    name = "libxau"
    version = tools.get_env("GIT_TAG", "1.0.9")
    description = "X11 authorisation library"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"
    generators = "env"

    def build_requirements(self):
        self.build_requires("env-generator/1.0.0@%s/stable" % self.user)
        self.build_requires("gcc/[>=7.4.0]@%s/stable" % self.user)
        self.build_requires("pkgconf/[>=1.6.3]@%s/stable" % self.user)

    def requirements(self):
        self.requires("xorgproto/[>=2019.1]@%s/stable" % self.user)

    def source(self):
        tools.get("https://xorg.freedesktop.org/releases/individual/lib/libXau-%s.tar.gz" % self.version)

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("libXau-" + self.version):
            autotools.configure(args=args)
            autotools.install()
