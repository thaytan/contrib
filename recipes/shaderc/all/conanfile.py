import os
from conans import *


class LibShadercConan(ConanFile):
    description = "A collection of tools, libraries, and tests for Vulkan shader compilation."
    license = "Apache"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build", "python"
    build_requires = ("cmake/[^3.18.4]",)

    def build_requirements(self):
        self.build_requires(f"python/[~{self.settings.python}]")

    def source(self):
        shaderc_git_dir = f"shaderc-{self.version}"
        git = tools.Git(folder=shaderc_git_dir)
        git.clone("https://github.com/google/shaderc", f"v{self.version}")
        self.run(f"cd {shaderc_git_dir} && ./utils/git-sync-deps")

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder=f"shaderrc-{self.version}")
        cmake.build()
        cmake.install()

    def package_info(self):
        self.env_info.SHADERC_LIB_DIR.append(os.path.join(self.package_folder, "lib"))
