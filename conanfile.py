from conans import ConanFile, AutoToolsBuildEnvironment, tools
from os import path, remove
from glob import glob

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "2.10.1"
    except:
        return None

class FreetypeConan(ConanFile):
    name = "freetype"
    version = get_version()
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "FreeType is a software library to render fonts"
    license = "GPL2"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def build_requirements(self):
        self.build_requires("env-generator/[>=0.1]@%s/stable" % self.user)
        self.build_requires("autotools/[>=1.0.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://git.savannah.gnu.org/cgit/freetype/freetype2.git/snapshot/freetype2-VER-%s.tar.gz" % self.version.replace(".", "-"))

    def build(self):
        args = [
            "--disable-static"
        ]
        with tools.chdir("freetype2-VER-" + self.version.replace(".", "-")):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.install()
        for f in glob(path.join(self.package_folder, "**", "*.la"), recursive=True):
            remove(f)

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.srcdirs.append("src")
