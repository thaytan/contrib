import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class BinutilsConan(ConanFile):
    name = "binutils"
    version = tools.get_env("GIT_TAG", "2.33.1")
    settings = "os", "compiler", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "GPL"
    description = "A set of programs to assemble and manipulate binary and object files"

    def build_requirements(self):
        self.build_requires("bootstrap-gcc/7.4.0@%s/stable" % self.user)

    def source(self):
        tools.get("https://ftp.gnu.org/gnu/binutils/binutils-{0}.tar.xz".format(self.version))

    def build(self):
        args = [
            "--enable-deterministic-archives",
            "--enable-gold",
            "--enable-ld=default",
            "--enable-lto",
            "--enable-plugins",
            "--enable-relro",
            "--enable-shared",
            "--enable-threads",
            "--disable-gdb",
            "--disable-werror",
            "--with-pic",
            "--with-system-zlib",
        ]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make(target="configure-host")
            autotools.make(["tooldir=" + self.package_folder])
            autotools.install(["tooldir=" + self.package_folder])
