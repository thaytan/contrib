import os
import shutil
from conans import *


class GlibcConan(ConanFile):
    description = "glibc"
    license = "GPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    requires = ("linux-headers/[^5.4.50]",)
    build_requires = ("bootstrap-glibc/[^2.27]",)

    def package(self):
        bootstrap_glibc_path = self.deps_cpp_info["bootstrap-glibc"].rootpath
        # Copy include lib and include
        folders = [
            "include",
            "lib",
        ]
        for folder in folders:
            src_folder = os.path.join(bootstrap_glibc_path, folder)
            dst_folder = os.path.join(self.package_folder, folder)
            shutil.copytree(src_folder, dst_folder)

    def package_info(self):
        self.env_info.LIBC_LIBRARY_PATH = os.path.join(self.package_folder, "lib")
