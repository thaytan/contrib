from conans import ConanFile, AutoToolsBuildEnvironment, tools
from os import remove, path
from glob import glob

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "2.6.1"
    except:
        return None

class HarfbuzzConan(ConanFile):
    name = "harfbuzz"
    version = get_version()
    license = "Old MIT"
    description = "HarfBuzz text shaping engine"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    settings = "os", "compiler", "build_type", "arch"
    generators = "env"

    def build_requirements(self):
        self.build_requires("env-generator/[>=0.1]@%s/stable" % self.user)
        self.build_requires("autotools/[>=1.0.0]@%s/stable" % self.user)
        self.build_requires("freetype-no-harfbuzz/[>=2.10.1]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/harfbuzz/harfbuzz/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--disable-static"]
        with tools.chdir("%s-%s" % (self.name , self.version)):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.install()
        for f in glob(path.join(self.package_folder, "**", "*.la"), recursive=True):
            remove(f)

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.cpp", "src")
            self.copy("*.hpp", "src")
