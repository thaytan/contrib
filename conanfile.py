from conans import ConanFile, tools

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "1.0.0"
    except:
        return None

class AutotoolsConan(ConanFile):
    name = "autotools"
    version = get_version()
    settings = "os", "compiler", "build_type", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "GPL"
    description = "A suite of programming tools 'designed' to assist in making source code"
    generators = "env"

    def requirements(self):
        self.requires("autoconf/2.69@%s/stable" % self.user)
        self.requires("automake/1.16.1@%s/stable" % self.user)
        self.requires("libtool/2.4.6@%s/stable" % self.user)
        self.requires("texinfo/6.6@%s/stable" % self.user)
