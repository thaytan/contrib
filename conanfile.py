from conans import ConanFile, tools, AutoToolsBuildEnvironment
from os import path, remove
from glob import glob

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "1.0.3"
    except:
        return None

class LibuuidConan(ConanFile):
    name = "libuuid"
    version = get_version()
    settings = "os", "compiler", "build_type", "arch"
    url = "https://github.com/prozum/conan-" + name
    license = "BSD-3-Clause"
    description = "Portable uuid C library"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/stable" % self.user)

    def source(self):
        tools.get("https://netix.dl.sourceforge.net/project/libuuid/libuuid-%s.tar.gz" % self.version)

    def build(self):
        args = [
            "--disable-static",
        ]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
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
