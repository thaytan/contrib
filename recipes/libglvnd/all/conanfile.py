import os
from conans import *


class LibglvndConan(ConanFile):
    description = "The GL Vendor-Neutral Dispatch library"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("meson/[^0.55.3]",)
    options = {
        "x11": [True, False],
    }
    default_options = ("x11=True",)

    def build_requirements(self):
        if self.options.x11:
            self.build_requires("xorgproto/[^2020.1]")

    def source(self):
        tools.get(f"https://gitlab.freedesktop.org/glvnd/libglvnd/-/archive/v{self.version}/libglvnd-v{self.version}.tar.gz")

    def build(self):
        args = [
            "--auto-features=disabled",
        ]

        meson = Meson(self)
        meson.configure(args, source_folder=f"libglvnd-v{self.version}", pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()

    def package_info(self):
        self.env_info.__EGL_VENDOR_LIBRARY_DIRS.append("/usr/share/glvnd/egl_vendor.d")
