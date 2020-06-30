import os

from conans import ConanFile, Meson, tools


class LibVaConan(ConanFile):
    description = "Libva is an implementation for VA-API (VIdeo Acceleration API)"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    options = {"x11": [True, False], "wayland": [True, False]}
    default_options = ("x11=True", "wayland=False")

    def build_requirements(self):
        self.build_requires("generators/1.0.0")
        self.build_requires("meson/[^0.51.2]")

    def requirements(self):
        self.requires("libdrm/[^2.4.96]")
        self.requires("libx11/[^1.6.8]")
        self.requires("libxext/[^1.3.4]")
        self.requires("libxfixes/[^5.0.3]")

    def source(self):
        tools.get("https://github.com/intel/libva/archive/%s.tar.gz" % self.version)

    def build(self):
        meson = Meson(self)
        args = ["--auto-features=disabled"]
        args.append("-Dwith_x11=" + ("yes" if self.options.x11 else "no"))
        args.append("-Dwith_wayland=" + ("yes" if self.options.wayland else "no"))
        meson.configure(
            source_folder="%s-%s" % (self.name, self.version), pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"),
        )
        meson.install()
