from conans import ConanFile, CMake, tools
import os

class GstreamerColorizerConan(ConanFile):
    name = "gstreamer-colorizer"
    license = "LGPL"
    description = "Plugin to colorize 16 bit grayscale depth images with a color map"
    url = "https://aivero.com"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ["CMakeLists.txt", "src/*"]

    def set_version(self):
        git = tools.Git(folder=self.recipe_folder)
        tag, branch = git.get_tag(), git.get_branch()
        self.version = tag if tag and branch.startswith("HEAD") else branch

    def build_requirements(self):
        self.build_requires("cmake/[>=3.15.3]@%s/stable" % (self.user))

    def requirements(self):
        gst_version = "[~1]"

        self.requires("gstreamer-plugins-base/%s@%s/stable" % (gst_version, self.user))

    def build(self):
        env = {
            "GIT_PKG_VER": "%s" % self.version,
        }
        with tools.environment_append(env):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()
            cmake.install()

    def package_info(self):
        self.env_info.GST_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
