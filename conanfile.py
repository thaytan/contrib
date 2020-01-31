import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class GccConan(ConanFile):
    name = "gcc"
    version = tools.get_env("GIT_TAG", "7.4.0")
    settings = "os", "compiler", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "custom", "FDL", "GPL", "LGPL"
    description = "The GNU Compiler Collection - C and C++ frontends"

    def build_requirements(self):
        self.build_requires("bootstrap-gcc/[>=7.4.0]@%s/stable" % self.user)
        self.build_requires("make/[>=4.3]@%s/stable" % self.user)

    def requirements(self):
        self.requires("binutils/[>=2.33.1]@%s/stable" % self.user)
        self.requires("isl/[>=0.22.1]@%s/stable" % self.user)

    def source(self):
        tools.get("https://ftp.gnu.org/gnu/gcc/gcc-{0}/gcc-{0}.tar.xz".format(self.version))

    def build(self):
        args = [
            "--libexecdir=%s" % os.path.join(self.package_folder, "lib"),
            "--disable-bootstrap",
            "--enable-languages=c,c++",
            "--enable-shared",
            "--enable-threads=posix",
            "--with-system-zlib",
            "--with-isl",
            "--disable-multilib",
            "--enable-__cxa_atexit",
            "--disable-libunwind-exceptions",
            "--enable-clocale=gnu",
            "--disable-libstdcxx-pch",
            "--disable-libssp",
            "--enable-gnu-unique-object",
            "--enable-linker-build-id",
            "--enable-lto",
            "--enable-plugin",
            "--enable-install-libiberty",
            "--with-linker-hash-style=gnu",
            "--enable-gnu-indirect-function",
            "--disable-werror",
            "--enable-checking=release",
            "--enable-default-pie",
            "--enable-default-ssp",
            "--enable-cet=auto",
        ]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.make(target="install-strip")

    def package_info(self):
        self.env_info.CC = os.path.join(self.package_folder, "bin", "gcc")
        self.env_info.CXX = os.path.join(self.package_folder, "bin", "g++")
