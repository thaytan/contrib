from build import *


class LibShadercRecipe(Recipe):
    description = "A collection of tools, libraries, and tests for Vulkan shader compilation."
    license = "Apache"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build", "python"
    build_requires = ("cmake/[^3.18.4]",)

    def build_requirements(self):
        self.build_requires(f"python/[~{self.settings.python}]")

    def source(self):
        self.get(f"https://github.com/google/shaderc/archive/v{self.version}.tar.gz")
        self.run(f"sh utils/git-sync-deps", cwd=f"{self.name}-{self.version}")

    def package_info(self):
        self.env_info.SHADERC_LIB_DIR.append(os.path.join(self.package_folder, "lib"))
