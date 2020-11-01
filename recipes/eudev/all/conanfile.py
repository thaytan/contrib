from conans import *


class EudevRecipe(Recipe):
    description = "OpenRC compatible fork of systemd-udev"
    license = "GPL2"
    build_requires = (
        "cc/[^1.0.0]",
        "autotools/[^1.0.0]",
        "gperf/[^3.1]",
        "gobject-introspection/[^1.59.3]",
    )

    def source(self):
        self.get(f"https://dev.gentoo.org/~blueness/eudev/eudev-{self.version}.tar.gz")
