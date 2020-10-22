import os
from conans import *


class LibvaConan(ConanFile):
    description = "Libva is an implementation for VA-API (Video Acceleration API)"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    options = {"x11": [True, False], "wayland": [True, False]}
    default_options = ("x11=True", "wayland=False")
    build_requires = (
        "cc/[^1.0.0]",
        "meson/[^0.55.3]",
    )
    requires = (
        "libdrm/[^2.4.102]",
        "libxext/[^1.3.4]",
        "libxfixes/[^5.0.3]",
    )

    def source(self):
        tools.get(f"https://github.com/intel/libva/archive/{self.version}.tar.gz")

    def build(self):
        meson = Meson(self)
        args = ["--auto-features=disabled"]
        args.append("-Dwith_x11=" + ("yes" if self.options.x11 else "no"))
        args.append("-Dwith_wayland=" + ("yes" if self.options.wayland else "no"))
        meson.configure(args, source_folder=f"libva-{self.version}", pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()
