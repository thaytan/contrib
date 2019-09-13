from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "1.19.1"
    except:
        return None

class LibXorgUtilMacrosConan(ConanFile):
    name = "xorg-util-macros"
    version = get_version()
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "custom"
    description = "X.Org Autotools macros"
    settings = "os", "compiler", "build_type", "arch"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/freedesktop/xorg-macros/archive/util-macros-%s.tar.gz" % self.version)

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("xorg-macros-util-macros-" + self.version):
            self.run("autoreconf -i")
            autotools.configure()
            autotools.install()

    def package_info(self):
        self.env_info.ACLOCAL_PATH.append(os.path.join(self.package_folder, "share", "aclocal"))
