from conans import AutoToolsBuildEnvironment, ConanFile, tools


class YasmConan(ConanFile):
    name = "yasm"
    version = tools.get_env("GIT_TAG", "1.3.0")
    description = "Yasm is a complete rewrite of the NASM assembler under the “new” BSD License"
    license = "BSD"
    settings = "os_build", "arch_build", "compiler"

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
