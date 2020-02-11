from conans import AutoToolsBuildEnvironment, ConanFile, tools


class Libxxf86vmConan(ConanFile):
    name = "libxxf86vm"
    version = tools.get_env("GIT_TAG", "1.1.4")
    description = "X11 XFree86 video mode extension library"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "custom"
    settings = "os", "compiler", "build_type", "arch"
    generators ="pkgconf"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("pkgconf/[>=1.6.3]@%s/stable" % self.user)
        self.build_requires("xorg-util-macros/[>=1.19.1]@%s/stable" % self.user)
        self.build_requires("xorgproto/[>=2019.1]@%s/stable" % self.user)

    def requirements(self):
        self.requires("libxext/[>=1.3.4]@%s/stable" % self.user)

    def source(self):
        tools.get("https://xorg.freedesktop.org/releases/individual/lib/libXxf86vm-%s.tar.gz" % self.version)

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("libXxf86vm-" + self.version):
            autotools.configure()
            autotools.install()
