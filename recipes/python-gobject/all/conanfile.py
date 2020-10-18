import os

from conans import *


class PythonGobjectConan(ConanFile):
    description = "Python GObject bindings"
    license = "LGPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("meson/[^0.51.2]",)
    requires = (
        "gobject-introspection/[^1.59.3]",
        "python-cairo/[^1.18.2]",
    )

    def source(self):
        tools.get(f"https://gitlab.gnome.org/GNOME/pygobject/-/archive/{self.version}/pygobject-{self.version}.tar.gz")

    def build(self):
        args = ["--auto-features=disabled", "--wrap-mode=nofallback"]
        meson = Meson(self)
        meson.configure(source_folder="pygobject-" + self.version, args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()
