from build import *


class GObjectIntrospectionRecipe(Recipe):
    description = "Middleware layer between C libraries (using GObject) and language bindings"
    license = "LGPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build", "python"
    build_requires = (
        "meson/[^0.55.3]",
        "bison/[^3.7.2]",
        "flex/[^2.6.4]",
        "git/[^2.28.0]",
    )
    requires = ("glib/[^2.66.1]",)

    def requirements(self):
        self.requires(f"python/[~{self.settings.python}]")

    def source(self):
        self.get(f"https://github.com/GNOME/gobject-introspection/archive/{self.version}.tar.gz")

    def package_info(self):
        self.env_info.PYTHONPATH = os.path.join(self.package_folder, "lib", "gobject-introspection")
