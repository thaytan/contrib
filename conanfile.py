from conans import AutoToolsBuildEnvironment, ConanFile, tools


class LibxdamageConan(ConanFile):
    name = "libxdamage"
    version = tools.get_env("GIT_TAG", "1.1.5")
    description = "X11 damaged region extension library"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "custom"
    settings = "os", "compiler", "build_type", "arch"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("pkgconf/[>=1.6.3]@%s/stable" % self.user)

    def requirements(self):
        self.requires("libxfixes/[>=5.0.3]@%s/stable" % self.user)

    def source(self):
        tools.get("https://xorg.freedesktop.org/releases/individual/lib/libXdamage-%s.tar.gz" % self.version)

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("libXdamage-" + self.version):
            autotools.configure()
            autotools.install()
