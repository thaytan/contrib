from build import *


class GObjectIntrospectionRecipe(PythonRecipe):
    description = "Middleware layer between C libraries (using GObject) and language bindings"
    license = "LGPL"
    build_requires = (
        "cc/[^1.0.0]",
        "meson/[>=0.55.3]",
        "bison/[^3.7.2]",
        "flex/[^2.6.4]",
        "python/[~3.8.5]",
    )
    requires = ("glib/[^2.66.1]",)

    def source(self):
        self.get(f"https://github.com/GNOME/gobject-introspection/archive/{self.version}.tar.gz")

    def package_info(self):
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "lib", "gobject-introspection"))
