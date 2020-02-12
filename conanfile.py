from conans import ConanFile, tools


class AutotoolsConan(ConanFile):
    name = "autotools"
    version = tools.get_env("GIT_TAG", "1.0.0")
    settings = "os", "compiler", "build_type", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "GPL"
    description = "A suite of programming tools 'designed' to assist in making source code"
    
    def requirements(self):
        self.requires("cc/[>=1.0.0]@%s/stable" % self.user)
        self.requires("make/[>=3.4.0]@%s/stable" % self.user)
        self.requires("autoconf/[>=2.69]@%s/stable" % self.user)
        self.requires("automake/[>=1.16.1]@%s/stable" % self.user)
        self.requires("libtool/[>=2.4.6]@%s/stable" % self.user)
        self.requires("pkgconf/[>=1.6.3]@%s/stable" % self.user)
        self.requires("gettext/[>=0.20.1]@%s/stable" % self.user)
        self.requires("texinfo/[>=6.6]@%s/stable" % self.user)
