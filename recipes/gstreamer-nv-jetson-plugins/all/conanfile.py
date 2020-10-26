from build import *


class GstreamerNvJetsonPluginsRecipe(Recipe):
    description = "Demo conan package"
    license = "MIT"
    exports_sources = ["lib/gstreamer-1.0/*.so"]

    def requirements(self):
        self.requires("nv-jetson-drivers/[^{self.version}]")

    def package(self):
        self.copy(pattern="*.so", excludes="*libgstnvvideo4linux2.so*")
