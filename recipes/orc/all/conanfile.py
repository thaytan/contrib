from conans import ConanFile, Meson, tools


class OrcConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    license = "LGPL-2.1"
    description = "Optimized Inner Loop Runtime Compiler"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("meson/[>=0.51.2]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/GStreamer/orc/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["-Dgtk_doc=disabled"]
        args.append("-Dbenchmarks=disabled")
        args.append("-Dexamples=disabled")
        meson = Meson(self)
        meson.configure(
            source_folder="orc-" + self.version,
            args=args,
            pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"),
        )
        meson.install()
