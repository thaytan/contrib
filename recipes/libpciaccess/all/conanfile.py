from conans import AutoToolsBuildEnvironment, ConanFile, tools


class LibPciAccessConan(ConanFile):
    description = "Generic PCI access library"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("env-generator/1.0.0")
        self.build_requires("xorg-util-macros/[^1.19.1]")

    def source(self):
        tools.get("https://xorg.freedesktop.org/releases/individual/lib/libpciaccess-%s.tar.gz" % self.version)

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools.configure(args=args)
            autotools.install()
