import pathlib
import os
import shutil
from conans import *


class BootstrapGlibcConan(ConanFile):
    description = "glibc bootstrap"
    license = "GPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    requires = "bootstrap-linux-headers/[^5.4.50]"

    def source(self):
        tools.get(f"https://ftp.gnu.org/gnu/glibc/glibc-{self.version}.tar.xz")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(configure_dir=f"glibc-{self.version}")
        autotools.make(target="install-headers")

        # install-headers does not create include/gnu/stubs.h
        pathlib.Path(os.path.join(self.package_folder, "include", "gnu", "stubs.h")).touch()

        # Use system libgcc_s
        arch = {"x86_64": "x86_64", "armv8": "aarch64"}[str(self.settings.arch_build)]
        os.makedirs(os.path.join(self.package_folder, "lib"))
        with tools.chdir(os.path.join(self.package_folder, "lib")):
            # Symlink to glibc
            libs = [
                "libc.so.6",
                "libm.so.6",
                "libdl.so.2",
                "librt.so.1",
                "libpthread.so.0",
                "libgcc_s.so.1",
            ]
            for lib in libs:
                os.symlink(f"/lib/{arch}-linux-gnu/{lib}", lib)
            # Copy from glibc-dev
            libs = [
                "libc.so",
                "libm.so",
                "libdl.so",
                "librt.so",
                "libpthread.so",
                "crt1.o",
                "crti.o",
                "crtn.o",
            ]
            for lib in libs:
                shutil.copy2(f"/usr/lib/{arch}-linux-gnu/{lib}", lib)
            # Copy libgcc_s from libgcc-7-dev
            shutil.copy2(f"/usr/lib/gcc/{arch}-linux-gnu/7/libgcc_s.so", "libgcc_s.so")

    def package_info(self):
        self.env_info.LIBC_LIBRARY_PATH = os.path.join(self.package_folder, "lib")
