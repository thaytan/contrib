from conans import AutoToolsBuildEnvironment, ConanFile, tools


class GitConan(ConanFile):
    description = "The fast distributed version control system"
    license = "GPL2"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("gcc/[^7.4.0]@%s/stable" % self.user)
        self.build_requires("gettext/[^0.20.1]@%s/stable" % self.user)

    def requirements(self):
        self.requires("zlib/[^1.2.11]@%s/stable" % self.user)
        self.requires("curl/[^7.66.0]@%s/stable" % self.user)
        self.requires("openssl/[^1.1.1b]@%s/stable" % self.user)

    def source(self):
        tools.get("https://www.kernel.org/pub/software/scm/git/git-%s.tar.xz" % self.version)

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.install()
