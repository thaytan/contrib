from conans import AutoToolsBuildEnvironment, ConanFile, tools


class ZlibConan(ConanFile):
    name = "zlib"
    version = tools.get_env("GIT_TAG", "1.2.11")
    url = "https://gitlab.com/aivero/public/conan/conan-zlib"
    license = "Zlib"
    description = (
        "A Massively Spiffy Yet Delicately Unobtrusive Compression Library "
        "(Also Free, Not to Mention Unencumbered by Patents)"
    )
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def build_requirements(self):
        self.build_requires("autotools/[>=1.0.0]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/madler/zlib/archive/v%s.tar.gz" % self.version)

    def build(self):
        args = ["--enable-shared"]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
