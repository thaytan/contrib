import os

from conans import *


class GccConan(ConanFile):
    description = "The GNU Compiler Collection - C and C++ frontends"
    license = "custom", "FDL", "GPL", "LGPL"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "bootstrap-gcc/[^7.4.0]",
        "make/[^4.3]",
    )
    requires = (
        "generators/[^1.0.0]",
        "binutils/[^2.33.1]",
        "isl/[^0.22.1]",
        "mpfr/[^4.0.2]",
        "mpc/[^1.1.0]",
    )

    def source(self):
        tools.get(f"https://ftp.gnu.org/gnu/gcc/gcc-{self.version}/gcc-{self.version}.tar.xz")

    def build(self):
        args = [
            "--libexecdir=" + os.path.join(self.package_folder, "lib"),
            "--disable-bootstrap",
            "--enable-languages=c,c++,objc,obj-c++",
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
        if self.settings.arch == "x86_64":
            target = "x86_64-linux-gnu"
        elif self.settings.arch == "armv8":
            target = "aarch64-linux-gnu"
        args.append("--build=" + target)
        args.append("--host=" + target)
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.make(target="install-strip")

    def package_info(self):
        self.env_info.CC = os.path.join(self.package_folder, "bin", "gcc")
        self.env_info.CXX = os.path.join(self.package_folder, "bin", "g++")
        # Needed for building Python modules
        ldshared = os.path.join(self.package_folder, "bin", "gcc") + " -pthread -shared "
        if self.settings.arch == "x86_64":
            ldshared += "-m64 "
        self.env_info.LDSHARED = ldshared
