from conans import AutoToolsBuildEnvironment, ConanFile, tools


class LibffiConan(ConanFile):
    name = "libffi"
    version = tools.get_env("GIT_TAG", "3.3-rc0")
    settings = "os", "compiler", "build_type", "arch"
    license = "MIT"
    description = "A portable, high level programming interface to various calling conventions"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("autotools/[>=1.0.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/libffi/libffi/archive/v%s.tar.gz" % self.version)

    def build(self):
        args = [
            "--quiet",
            "--disable-debug",
            "--disable-dependency-tracking",
            "--disable-docs",
            "--disable-static",
            "--enable-shared",
        ]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
