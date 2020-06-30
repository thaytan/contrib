import os

from conans import CMake, ConanFile, tools


class LibShadercConan(ConanFile):
    description = "A collection of tools, libraries, and tests for Vulkan shader compilation."
    license = "Apache"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0")
        self.build_requires("gcc/[^7.4.0]")
        self.build_requires("cmake/[^3.15.3]")
        self.requires("python/[^3.7.4]")

    def source(self):
        shaderc_git_dir = "shaderc-%s" % self.version
        git = tools.Git(folder=shaderc_git_dir)
        git.clone("https://github.com/google/shaderc", "v%s" % self.version)
        self.run("cd %s && ./utils/git-sync-deps" % shaderc_git_dir)

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.configure(source_folder="%s-%s" % (self.name, self.version))
        cmake.build()
        cmake.install()

    def package_info(self):
        self.env_info.SHADERC_LIB_DIR.append(os.path.join(self.package_folder, "lib"))
