from conans import AutoToolsBuildEnvironment, ConanFile, tools


class LibSrtpConan(ConanFile):
    name = "libsrtp"
    version = tools.get_env("GIT_TAG", "2.2.0")
    url = "http://gitlab.com/aivero/public/conan/conan-" + name
    license = "BSD"
    description = "Library for SRTP (Secure Realtime Transport Protocol)"
    settings = "os", "arch", "compiler", "build_type"
    generators ="pkgconf"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/cisco/libsrtp/archive/v%s.tar.gz" % self.version)

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make(args=["shared_library"])
            autotools.install()
