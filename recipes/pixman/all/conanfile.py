from conans import ConanFile, Meson, tools


class PixmanConan(ConanFile):
    description = "Image processing and manipulation library"
    license = "custom"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("meson/[>=0.51.2]@%s/stable" % self.user)

    def source(self):
        tools.get("https://xorg.freedesktop.org/releases/individual/lib/pixman-%s.tar.bz2" % self.version)

    def build(self):
        args = ["--auto-features=disabled"]
        meson = Meson(self)
        meson.configure(
            source_folder="%s-%s" % (self.name, self.version), args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"),
        )
        meson.install()
