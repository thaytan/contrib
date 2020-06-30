from conans import AutoToolsBuildEnvironment, ConanFile, tools


class LibSrtpConan(ConanFile):
    description = "Library for SRTP (Secure Realtime Transport Protocol)"
    license = "BSD"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0")

    def source(self):
        tools.get("https://github.com/cisco/libsrtp/archive/v%s.tar.gz" % self.version)

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make(args=["shared_library"])
            autotools.install()
