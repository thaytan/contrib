import os

from conans import *


class GLibConan(ConanFile):
    description = "GLib provides the core application building blocks for libraries and applications written in C"
    license = "LGPL2.1"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("meson/[^0.55.3]",)
    requires = (
        "libffi/[^3.3]",
        "zlib/[^1.2.11]",
    )

    def source(self):
        tools.get(f"https://github.com/GNOME/glib/archive/{self.version}.tar.gz")

    def build(self):
        args = [
            "--auto-features=disabled",
            "-Dman=False",
            "-Dgtk_doc=False",
            "-Dinternal_pcre=False",
        ]
        meson = Meson(self)
        meson.configure(args, source_folder=f"glib-{self.version}", pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()
