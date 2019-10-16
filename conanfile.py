import os

from conans import ConanFile, tools


class GstreamerNvJetsonPluginsConan(ConanFile):
    name = "gstreamer-nv-jetson-plugins"
    version = tools.get_env("GIT_TAG", "32.2.1")
    url = "http://gitlab.com/aivero/public/conan/conan-" + name
    license = "MIT"
    description = "Demo conan package"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ["lib/gstreamer-1.0/*.so"]
    generators = "env"

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.requires("jetson-drivers/[>=%s]@%s/stable" % (self.version, self.user))

    def package(self):
        self.copy("*.so")

    def package_info(self):
        self.env_info.GST_PLUGIN_PATH.append(
            os.path.join(self.package_folder, "lib", "gstreamer-1.0")
        )
