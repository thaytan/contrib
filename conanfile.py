from conans import ConanFile, AutoToolsBuildEnvironment, tools
from glob import glob
from os import path, remove

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "2.10.1"
    except:
        return None

class FreetypeNoHarfbuzzConan(ConanFile):
    name = "freetype-no-harfbuzz"
    version = get_version()
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "FreeType is a software library to render fonts"
    license = "GPL2"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/stable" % self.user)

    def source(self):
        tools.get("https://git.savannah.gnu.org/cgit/freetype/freetype2.git/snapshot/freetype2-VER-%s.tar.gz" % self.version.replace(".", "-"))

    def build(self):
        args = [
            "--disable-static"
        ]
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("freetype2-VER-" + self.version.replace(".", "-")):
            self.run("./autogen.sh")
            autotools.configure(args=args)
            autotools.install()
        for f in glob(path.join(self.package_folder, "**", "*.la"), recursive=True):
            remove(f)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
