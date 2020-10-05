import os

from conans import *


class BootstrapGccConan(ConanFile):
    description = "The GNU Compiler Collection - C and C++ frontends"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"

    def source(self):
        tools.get(f"https://ftp.gnu.org/gnu/gcc/gcc-{self.version}/gcc-{self.version}.tar.xz")

    def build(self):
        args = [
            f"--libexecdir={os.path.join(self.package_folder, 'lib')}",
            "--disable-bootstrap",
            "--disable-multilib",
            "--enable-languages=c,c++,objc,obj-c++",
            "--enable-threads=posix",
            "--enable-__cxa_atexit",
            "--disable-libunwind-exceptions",
            "--enable-clocale=gnu",
            "--disable-libstdcxx-pch",
            "--disable-libssp",
            "--enable-gnu-unique-object",
            "--enable-linker-build-id",
            "--enable-install-libiberty",
            "--with-linker-hash-style=gnu",
            "--enable-gnu-indirect-function",
            "--disable-werror",
            "--enable-checking=release",
            "--enable-default-pie",
            "--enable-default-ssp",
            "--enable-cet=auto",
            "--with-system-zlib",
            # f"--with-mpfr={self.deps_cpp_info['mpfr'].rootpath}",
            # f"--with-gmp={self.deps_cpp_info['gmp'].rootpath}",
            # f"--with-mpc={self.deps_cpp_info['mpc'].rootpath}",
            # f"--with-isl={self.deps_cpp_info['isl'].rootpath}",
        ]
        if self.settings.arch_build == "x86_64":
            target = "x86_64-linux-gnu"
        elif self.settings.arch_build == "armv8":
            target = "aarch64-linux-gnu"
        args.append(f"--build={target}")
        args.append(f"--host={target}")
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"{self.name}-{self.version}", args)
        autotools.make()
        autotools.install()
