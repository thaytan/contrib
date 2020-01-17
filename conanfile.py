import glob
import os

from conans import ConanFile, tools


class BinutilsConan(ConanFile):
    name = "binutils"
    version = tools.get_env("GIT_TAG", "2.30")
    settings = "os", "compiler", "build_type", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "GPL"
    description = "A set of programs to assemble and manipulate binary and object files"
    generators = "env"

    def build_requirements(self):
        self.build_requires("env-generator/1.0.0@%s/stable" % self.user)

    def source(self):
        if self.settings.arch == "x86_64":
            arch_binutils = "https://mex.mirror.pkgbuild.com/core/os/x86_64/binutils-2.32-3-x86_64.pkg.tar.xz"
            binutils = "http://security.ubuntu.com/ubuntu/pool/main/b/binutils/binutils-x86-64-linux-gnu_2.30-21ubuntu1~18.04.2_amd64.deb"
            libbinutils = "http://security.ubuntu.com/ubuntu/pool/main/b/binutils/libbinutils_2.30-21ubuntu1~18.04.2_amd64.deb"
        elif self.settings.arch == "armv8":
            arch_binutils = "http://mirror.archlinuxarm.org/aarch64/core/binutils-2.32-1-aarch64.pkg.tar.xz"
            binutils = "http://ports.ubuntu.com/ubuntu-ports/pool/main/b/binutils/binutils-aarch64-linux-gnu_2.30-21ubuntu1~18.04.2_arm64.deb"
            libbinutils = "http://ports.ubuntu.com/ubuntu-ports/pool/main/b/binutils/libbinutils_2.30-21ubuntu1~18.04.2_arm64.deb"
        tools.get(arch_binutils)
        tools.download(binutils, filename="binutils.deb")
        tools.download(libbinutils, filename="libbinutils.deb")

    def build(self):
        env = {"LD_LIBRARY_PATH": "usr/lib", "PATH": "usr/bin"}
        with tools.environment_append(env):
            for pkg in ("binutils", "libbinutils"):
                self.run("ar x %s.deb" % pkg)
                tools.unzip("data.tar.xz", destination="data")
        with tools.chdir("data/usr/bin"):
            for lib in glob.glob("*-linux-gnu-*"):
                os.symlink(lib, lib.split("-")[-1])
        tools.rmdir("usr")

    def package(self):
        self.copy("*", dst="bin", src="data/usr/bin", symlinks=True)
        self.copy("*.so", dst="lib", src="data/usr/lib", keep_path=False)
