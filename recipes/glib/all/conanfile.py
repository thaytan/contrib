import os

from conans import *


class GLibConan(ConanFile):
    description = "GLib provides the core application building blocks for libraries and applications written in C"
    license = "LGPL2.1"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "meson/[^0.55.3]",
        "cc/[^1.0.0]",
    )
    requires = (
        "libffi/[^3.3]",
        "zlib/[^1.2.11]",
    )

    def source(self):
        tools.get(f"https://github.com/GNOME/glib/archive/{self.version}.tar.gz")
        # Disable broken gio tests until fixed by upstream (https://gitlab.gnome.org/GNOME/glib/issues/1897)
        # Use tools.replace_in_file()
        # self.run(f"sed glib-{self.version}/gio/meson.build -i -e 's/build_tests = .*/build_tests = false/'")

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
