from conans import AutoToolsBuildEnvironment, ConanFile, tools


def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "0.9.10"
    except:
        return None

class LibxrenderConan(ConanFile):
    name = "libxrender"
    version = get_version()
    description = "X Rendering Extension client library"
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
        self.requires("libx11/[>=1.6.8]@%s/stable" % self.user)
        self.requires("renderproto/[>=0.11.1]@%s/stable" % self.user)

    def source(self):
        tools.get("https://xorg.freedesktop.org/releases/individual/lib/libXrender-%s.tar.gz" % self.version)
        with tools.chdir("libXrender-" + self.version):
            tools.download("http://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f=config.guess;hb=HEAD", "config.guess", overwrite=True)
            tools.download("http://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f=config.sub;hb=HEAD", "config.sub", overwrite=True)

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("libXrender-" + self.version):
            autotools.configure(args=args)
            autotools.install()
