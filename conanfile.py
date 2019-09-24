from conans import ConanFile, tools, AutoToolsBuildEnvironment
from os import path, symlink, remove
from glob import glob

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "0.20.1"
    except:
        return None

class GettextConan(ConanFile):
    name = "gettext"
    version = get_version()
    settings = "os", "compiler", "build_type", "arch"
    url = "https://github.com/prozum/conan-" + name
    license = "GPL"
    description = "GNU internationalization library"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/stable" % self.user)

    def source(self):
        tools.get("https://ftp.gnu.org/pub/gnu/gettext/gettext-%s.tar.gz" % self.version)

    def build(self):
        args = [
            "--disable-static"
        ]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
        symlink("preloadable_libintl.so", path.join(self.package_folder, "lib", "libpreloadable_libintl.so"))
        symlink("preloadable_libintl.so", path.join(self.package_folder, "lib", "libgnuintl.so.8"))
        for f in glob(path.join(self.package_folder, "**", "*.la"), recursive=True):
            remove(f)

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.srcdirs.append("src")
        self.env_info.gettext_datadir.append(path.join(self.package_folder, "share", "gettext"))
