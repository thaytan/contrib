import os
from conans import *


class HarfbuzzConan(ConanFile):
    description = "HarfBuzz text shaping engine"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "cc/[^1.0.0]",
        "meson/[^0.55.3]",
        "freetype/[^2.10.3]",
        "gobject-introspection/[^1.66.1]",
    )
    requires = ("glib/[^2.66.1]",)

    def configure(self):
        # Avoid circular requirement
        self.options["freetype"].harfbuzz = False

    def source(self):
        tools.get(f"https://github.com/harfbuzz/harfbuzz/archive/{self.version}.tar.gz")

    def build(self):
        args = [
            "--auto-features=disabled",
            "-Dfreetype=enabled",
            "-Dgobject=enabled",
            "-Dintrospection=enabled",
        ]
        meson = Meson(self)
        meson.configure(args, source_folder=f"harfbuzz-{self.version}", pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()
