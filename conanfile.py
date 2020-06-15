import os

from conans import CMake, ConanFile, tools

class LibShadercConan(ConanFile):
    name = "shaderc"
    version = tools.get_env("GIT_TAG", "2020.1")
    license = "Apache"
    description = "A collection of tools, libraries, and tests for Vulkan shader compilation."
    settings = "os", "compiler", "build_type", "arch"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("gcc/[>=7.4.0]@%s/stable" % self.user)
        self.build_requires("cmake/[>=3.15.3]@%s/stable" % self.user)
        self.requires("python/[>=3.7.4]@%s/stable" % self.user)

    def requirements(self):
        # Maybe something here
        a = 0

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
        self.env_info.SHADERC_LIB_DIR = os.path.join(self.package_folder, "libs")
