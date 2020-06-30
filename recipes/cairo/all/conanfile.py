import os

from conans import *


class CairoConan(ConanFile):
    description = "2D graphics library with support for multiple output devices"
    license = "LGPL"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    default_options = ("introspection=True", "zlib=True", "png=True", "fontconfig=True")
    scm = {
        "type": "git",
        "url": "https://github.com/centricular/cairo.git",
        "revision": "meson-" + version,
        "recursive": True,
        "subfolder": f"cairo-{version}",
    }
    build_requires = (
        "generators/1.0.0",
        "meson/[^0.51.2]",
        "gobject-introspection/[^1.59.3]",
    )
    requires = (
        "glib/[^2.62.0]",
        "pixman/[^0.38.4]",
        "libxrender/[^0.9.10]",
        "libxext/[^1.3.4]",
        "fontconfig/[^2.13.1]",
        "zlib/[^1.2.11]",
        "libpng/[^1.6.37]",
    )

    def build(self):
        meson = Meson(self)
        args = ["-Dintrospection=" + ("enabled" if self.options.introspection else "disabled")]
        args.append("-Dfontconfig=" + ("enabled" if self.options.fontconfig else "disabled"))
        args.append("-Dzlib=" + ("enabled" if self.options.zlib else "disabled"))
        args.append("-Dpng=" + ("enabled" if self.options.png else "disabled"))
        meson.configure(source_folder=f"{self.name}-${self.version}", args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()

    def package_info(self):
        self.env_info.GI_TYPELIB_PATH.append(os.path.join(self.package_folder, "lib", "girepository-1.0"))
