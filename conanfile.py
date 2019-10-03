from conans import AutoToolsBuildEnvironment, ConanFile, tools


def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "1.6.8"
    except:
        return None

class Libx11Conan(ConanFile):
    name = "libx11"
    version = get_version()
    description = "X11 client-side library"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"
    generators = "env"

    def build_requirements(self):
        self.build_requires("pkgconf/[>=1.6.3]@%s/stable" % self.user)
        self.build_requires("xorg-util-macros/[>=1.19.1]@%s/stable" % self.user)
        self.build_requires("xtrans/[>=1.4.0]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.requires("xorgproto/[>=2019.1]@%s/stable" % self.user)
        self.requires("libxcb/[>=1.13.1]@%s/stable" % self.user)

    def source(self):
        tools.get("https://xorg.freedesktop.org/releases/individual/lib/libX11-%s.tar.gz" % self.version)

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("libX11-" + self.version):
            autotools.configure(args=args)
            autotools.install()
