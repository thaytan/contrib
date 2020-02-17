from conans import AutoToolsBuildEnvironment, ConanFile, tools


class LibpthreadStubsConan(ConanFile):
    name = "libpthread-stubs"
    version = tools.get_env("GIT_TAG", "0.4")
    description = "X11 client-side library"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)

    def source(self):
        tools.get("https://xcb.freedesktop.org/dist/libpthread-stubs-%s.tar.bz2" % self.version)

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools.configure()
            autotools.install()
