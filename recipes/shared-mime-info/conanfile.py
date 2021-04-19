tfrom build import *


class SharedMimeInfoRecipe(Recipe):
    description = "Freedesktop.org Shared MIME Info"
    license = "GPL"
    build_requires = (
        "cc/[^1.0.0]",
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
        self.get(f"https://gitlab.freedesktop.org/xdg/shared-mime-info/-/archive/{self.version}/shared-mime-info-{self.version}.tar.gz")
        tools.replace_in_file(os.path.join(self.src, "data", "meson.build"), "build_by_default: true", "build_by_default: false")

    def build(self):
        opts = {
          "update-mimedb": False,
        }
        self.meson(opts)
