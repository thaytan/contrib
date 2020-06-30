from conans import AutoToolsBuildEnvironment, ConanFile, tools


class LibunwindConan(ConanFile):
    description = "Portable and efficient C programming interface (API) to determine the call-chain of a programs"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0")
        self.build_requires("autotools/[^1.0.0]")

    def source(self):
        tools.get("https://download.savannah.gnu.org/releases/libunwind/libunwind-%s.tar.gz" % self.version)

    def build(self):
        args = [
            "--disable-static",
        ]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
