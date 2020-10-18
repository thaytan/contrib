import os

from conans import *


class LibShadercConan(ConanFile):
    description = "A collection of tools, libraries, and tests for Vulkan shader compilation."
    license = "Apache"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "cc/[^1.0.0]",
        "cmake/[^3.15.3]",
        "python/[^3.7.4]",
    )

    def source(self):
        shaderc_git_dir = f"shaderc-{self.version}"
        git = tools.Git(folder=shaderc_git_dir)
        git.clone("https://github.com/google/shaderc", f"v{self.version}")
        self.run(f"cd {shaderc_git_dir} && ./utils/git-sync-deps")

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.configure(source_folder=f"{self.name}-{self.version}")
        cmake.build()
        cmake.install()

    def package_info(self):
        self.env_info.SHADERC_LIB_DIR.append(os.path.join(self.package_folder, "lib"))
