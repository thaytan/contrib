from conans import AutoToolsBuildEnvironment, ConanFile, tools


class OpusConan(ConanFile):
    description = "Modern audio compression for the internet"
    license = "BSD"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

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
