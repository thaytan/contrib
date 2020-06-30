import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class BinutilsConan(ConanFile):
    name = "binutils"
    version = tools.get_env("GIT_TAG", "2.33.1")
    settings = "os", "compiler", "arch"
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
            autotools.make(["tooldir=" + self.package_folder], target="install-strip")

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
