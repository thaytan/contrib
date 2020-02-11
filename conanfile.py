from glob import glob
from os import path, remove, symlink

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class GettextConan(ConanFile):
    name = "gettext"
    version = tools.get_env("GIT_TAG", "0.20.1")
    settings = "os", "compiler", "build_type", "arch"
    url = "https://github.com/prozum/conan-" + name
    description = "GNU internationalization library"
    license = "GPL"
    generators ="pkgconf"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("gcc/[>=7.4.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://ftp.gnu.org/pub/gnu/gettext/gettext-%s.tar.gz" % self.version)

    def build(self):
        args = ["--disable-static"]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
        symlink(
            "preloadable_libintl.so",
            path.join(self.package_folder, "lib", "libpreloadable_libintl.so"),
        )
        symlink(
            "preloadable_libintl.so",
            path.join(self.package_folder, "lib", "libgnuintl.so.8"),
        )

    def package_info(self):
        self.env_info.gettext_datadir.append(path.join(self.package_folder, "share", "gettext"))
