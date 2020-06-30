from conans import AutoToolsBuildEnvironment, ConanFile, tools


class YasmConan(ConanFile):
    description = "Yasm is a complete rewrite of the NASM assembler under the “new” BSD License"
    license = "BSD"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("gcc/7.4.0@%s/stable" % self.user)

    def source(self):
        tools.get("http://www.tortall.net/projects/yasm/releases/yasm-%s.tar.gz" % self.version)

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.install()
