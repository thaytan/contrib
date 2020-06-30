from conans import AutoToolsBuildEnvironment, ConanFile, tools


class XcbProtoConan(ConanFile):
    name = "xcb-proto"
    version = tools.get_env("GIT_TAG", "1.13")
    description = "XML-XCB protocol descriptions"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("pkgconf/[>=1.6.3]@%s/stable" % self.user)

    def source(self):
        tools.get("https://xcb.freedesktop.org/dist/xcb-proto-%s.tar.bz2" % self.version)

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools.configure()
            autotools.install()
