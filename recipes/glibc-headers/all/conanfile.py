import os
import shutil
from conans import *


class GlibcHeadersConan(ConanFile):
    description = "glibc headers"
    license = "GPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    requires = ("linux-headers/[^5.4.50]",)
    build_requires = ("bootstrap-glibc-headers/[^2.27]",)

    def package(self):
        pkg_rootpath = self.deps_cpp_info["bootstrap-glibc-headers"].rootpath
        # Copy include
        include_folder = os.path.join(pkg_rootpath, "include")
        if os.path.exists(include_folder):
            shutil.copytree(include_folder, os.path.join(self.package_folder, "include"))
