from conans import AutoToolsBuildEnvironment, ConanFile, tools


class FlexConan(ConanFile):
    description = "Flex, the fast lexical analyzer generator"
    license = "BSD 2-Clause"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("autotools/[>=1.0.0]@%s/stable" % self.user)
        self.build_requires("bison/[>=3.3]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/westes/flex/releases/download/v{0}/flex-{0}.tar.gz".format(self.version))

    def build(self):
        args = ["--disable-nls", "ac_cv_func_reallocarray=no"]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.install()
