from build import *


class LibglvndRecipe(Recipe):
    description = "The GL Vendor-Neutral Dispatch library"
    license = "custom"
    options = {
        "x11": [True, False],
    }
    default_options = ("x11=True",)
    build_requires = (
        "cc/[^1.0.0]",
        "meson/[^0.55.3]",
    )

    def requirements(self):
        if self.options.x11:
            self.requires("libxext/[^1.3.4]", "private")
            self.requires("libx11/[^1.6.12]", "private")
            self.requires("xorgproto/[^2020.1]", "private")

    def source(self):
        self.get(f"https://gitlab.freedesktop.org/glvnd/libglvnd/-/archive/v{self.version}/libglvnd-v{self.version}.tar.gz")

    def build(self):
        opts = {
            "x11": self.options.x11,
            "glx": self.options.x11,
        }
        self.meson(opts)

    def package_info(self):
        self.env_info.__EGL_VENDOR_LIBRARY_DIRS.append("/usr/share/glvnd/egl_vendor.d")
