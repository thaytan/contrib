from conans import ConanFile, Meson, tools
import os

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "0.38.4"
    except:
        return None

class PixmanConan(ConanFile):
    name = "pixman"
    version = get_version()
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "Image processing and manipulation library"
    license = "https://gitlab.freedesktop.org/pixman/pixman/blob/master/COPYING"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/stable" % self.user)

    def source(self):
        tools.get("https://gitlab.freedesktop.org/pixman/pixman/-/archive/pixman-{0}/pixman-pixman-{0}.tar.gz".format(self.version))

    def build(self):
        args = ["--auto-features=disabled"]
        meson = Meson(self)
        meson.configure(source_folder="pixman-pixman-%s" % self.version, args=args)
        meson.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.srcdirs.append("src")
