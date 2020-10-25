import os
from conans import *


class SharedMimeInfoConan(ConanFile):
    description = "Freedesktop.org Shared MIME Info"
    license = "GPL2"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "meson/[^0.55.3]",
        "itstool/[^2.0.6]",
        "xz/[^5.2.4]",
        "gettext/[^0.21]",
        "xmlto/[^0.0.28]",
    )
    requires = (
        "glib/[^2.62.0]",
        "libxml2/[^2.9.9]",
    )

    def source(self):
        tools.get(f"https://gitlab.freedesktop.org/xdg/shared-mime-info/-/archive/{self.version}/shared-mime-info-{self.version}.tar.gz")
        tools.replace_in_file(os.path.join(f"shared-mime-info-{self.version}", "data", "meson.build"), "build_by_default: true", "build_by_default: false")

    def build(self):
        args = [
            "--auto-features=disabled",
            "--wrap-mode=nofallback",
            "-Dupdate-mimedb=false",
        ]
        meson = Meson(self)
        meson.configure(args, source_folder=f"shared-mime-info-{self.version}", pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()
