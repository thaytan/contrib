from build import *


class LibvaRecipe(Recipe):
    description = "Libva is an implementation for VA-API (Video Acceleration API)"
    license = "MIT"
    options = {"x11": [True, False], "wayland": [True, False]}
    default_options = ("x11=True", "wayland=False")
    build_requires = ("cc/[^1.0.0]", "meson/[^0.55.3]")
    requires = (
        "libdrm/[^2.4.102]",
        "libxext/[^1.3.4]",
        "libxfixes/[^5.0.3]",
    )

    def source(self):
        self.get(f"https://github.com/intel/libva/archive/{self.version}.tar.gz")

    def build(self):
        args = []
        args.append("-Dwith_x11=" + ("yes" if self.options.x11 else "no"))
        args.append("-Dwith_wayland=" + ("yes" if self.options.wayland else "no"))
        self.meson(args)
