from conans import AutoToolsBuildEnvironment, ConanFile, tools


class XtransConan(ConanFile):
    description = "X transport library"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)

    def source(self):
        tools.get(
            "https://xorg.freedesktop.org/releases/individual/lib/xtrans-%s.tar.gz"
            % self.version
        )

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools.configure()
            autotools.install()
