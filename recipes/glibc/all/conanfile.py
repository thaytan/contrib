import os
import shutil
from conans import *


class GlibcConan(ConanFile):
    description = "glibc"
    license = "GPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    requires = ("linux-headers/[^5.4.50]",)
    build_requires = ("bootstrap-glibc-headers/[^2.27]",)

    def package(self):
        pkg_rootpath = self.deps_cpp_info["bootstrap-glibc-headers"].rootpath
        # Copy include lib and include
        folders = [
            "include",
            "lib",
        ]
        for folder in folders:
            src_folder = os.path.join(pkg_rootpath, folder)
            dst_folder = os.path.join(self.package_folder, folder)
            shutil.copytree(src_folder, dst_folder)
