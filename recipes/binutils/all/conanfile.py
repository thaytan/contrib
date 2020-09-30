import os

from conans import *


class BinutilsConan(ConanFile):
    description = "A set of programs to assemble and manipulate binary and object files"
    license = "GPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "bootstrap-llvm/[^10.0.1]",
        "make/[^4.3]",
    )

    def source(self):
        tools.get(f"https://ftp.gnu.org/gnu/binutils/binutils-{self.version}.tar.xz")

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
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"{self.name}-{self.version}", args)
        autotools.make(target="configure-host")
        autotools.make([f"tooldir={self.package_folder}"])
        autotools.install([f"tooldir={self.package_folder}"])

    def package_info(self):
        self.env_info.LD = os.path.join(self.package_folder, "bin", "ld")
        self.env_info.AS = os.path.join(self.package_folder, "bin", "as")
        self.env_info.ADDR2LINE = os.path.join(self.package_folder, "bin", "addr2line")
        self.env_info.AR = os.path.join(self.package_folder, "bin", "ar")
        self.env_info.NM = os.path.join(self.package_folder, "bin", "nm")
        self.env_info.OBJCOPY = os.path.join(self.package_folder, "bin", "objcopy")
        self.env_info.OBJDUMP = os.path.join(self.package_folder, "bin", "objdump")
        self.env_info.RANLIB = os.path.join(self.package_folder, "bin", "ranlib")
        self.env_info.READELF = os.path.join(self.package_folder, "bin", "readelf")
        self.env_info.SIZE = os.path.join(self.package_folder, "bin", "size")
        self.env_info.STRINGS = os.path.join(self.package_folder, "bin", "strings")
        self.env_info.STRIP = os.path.join(self.package_folder, "bin", "strip")
