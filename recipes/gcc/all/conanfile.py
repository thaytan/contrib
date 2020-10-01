import os

from conans import *


class GccConan(ConanFile):
    description = "The GNU Compiler Collection - C and C++ frontends"
    license = "custom", "FDL", "GPL", "LGPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "bootstrap-llvm/[^10.0.1]",
        "binutils/[^2.35]",
        "make/[^4.3]",
        "zlib/[^1.2.11]",
        "mpfr/[^4.1.0]",
        "gmp/[^6.2.0]",
        "mpc/[^1.1.0]",
        "isl/[^0.22.1]",
    )

    def source(self):
        tools.get(f"https://ftp.gnu.org/gnu/gcc/gcc-{self.version}/gcc-{self.version}.tar.xz")

    def build(self):
        env = {
            "OBJDUMP": os.path.join(self.deps_cpp_info["binutils"].rootpath, "bin", "objdump"),
        }
        args = [
            f"--libexecdir={os.path.join(self.package_folder, 'lib')}",
            "--disable-bootstrap",
            "--enable-languages=c,c++,objc,obj-c++",
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
            f"--with-mpfr={self.deps_cpp_info['mpfr'].rootpath}",
            f"--with-gmp={self.deps_cpp_info['gmp'].rootpath}",
            f"--with-mpc={self.deps_cpp_info['mpc'].rootpath}",
            f"--with-isl={self.deps_cpp_info['isl'].rootpath}",
        ]
        if self.settings.arch_build == "x86_64":
            target = "x86_64-linux-gnu"
        elif self.settings.arch_build == "armv8":
            target = "aarch64-linux-gnu"
        args.append(f"--build={target}")
        args.append(f"--host={target}")
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"{self.name}-{self.version}", args, vars=env)
        autotools.make()
        autotools.install()
