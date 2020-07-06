from conans import *


class OrcConan(ConanFile):
    name = "orc"
    description = "Optimized Inner Loop Runtime Compiler"
    license = "LGPL-2.1"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    build_requires = ("meson/[^0.51.2]",)

    def source(self):
        tools.get(f"https://github.com/GStreamer/orc/archive/{self.version}.tar.gz")

    def build(self):
        args = ["-Dgtk_doc=disabled"]
        args.append("-Dbenchmarks=disabled")
        args.append("-Dexamples=disabled")
        meson = Meson(self)
        meson.configure(source_folder="orc-" + self.version, args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()
