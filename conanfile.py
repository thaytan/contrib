from conans import AutoToolsBuildEnvironment, ConanFile, tools


class OpusConan(ConanFile):
    name = "opus"
    version = tools.get_env("GIT_TAG", "1.3.1")
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "Modern audio compression for the internet"
    license = "BSD"
    settings = "os", "compiler", "build_type", "arch"
    generators ="pkgconf"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)

    def source(self):
        tools.get("https://archive.mozilla.org/pub/opus/opus-%s.tar.gz" % self.version)

    def build(self):
        args = ["--disable-static"]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.install()
