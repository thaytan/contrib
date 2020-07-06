from conans import *


class GperfConan(ConanFile):
    description = "A portable, high level programming interface to various calling conventions"
    license = "GPL3"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}

    def source(self):
        git = tools.Git(f"{self.name}-{self.version}")
        git.clone("https://gitlab.com/aivero/public/gperf.git", "meson")

    def build(self):
        meson = Meson(self)
        meson.configure(source_folder=f"{self.name}-{self.version}")
        meson.install()
