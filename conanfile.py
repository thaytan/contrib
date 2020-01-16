from conans import AutoToolsBuildEnvironment, ConanFile, tools


class LibxcbConan(ConanFile):
    name = "libxcb"
    version = tools.get_env("GIT_TAG", "1.13.1")
    description = "X11 client-side library"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"
    generators = "env"

    def build_requirements(self):
        self.build_requires("env-generator/1.0.0@%s/stable" % self.user)
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
