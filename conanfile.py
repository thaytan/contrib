import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class NcursesConan(ConanFile):
    name = "ncurses"
    version = tools.get_env("GIT_TAG", "6.1")
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "Zlib"
    description = "System V Release 4.0 curses emulation library"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def build_requirements(self):
        self.build_requires("env-generator/1.0.0@%s/stable" % self.user)
        self.build_requires("gcc/[>=7.4.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://ftp.gnu.org/pub/gnu/ncurses/ncurses-%s.tar.gz" % self.version)

    def build(self):
        args = [
            "--enable-overwrite",
            "--with-shared",
            "--with-cxx-shared",
            "--with-cxx-binding",
            "--enable-pc-files",
            "--with-pkg-config-libdir=%s" % os.path.join(self.package_folder, "lib", "pkgconfig"),
        ]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()

    def package_info(self):
        self.env_info.TERMINFO = os.path.join(self.package_folder, "share", "terminfo")
