import os

from conans import ConanFile, Meson, tools


class GObjectIntrospectionConan(ConanFile):
    description = "Middleware layer between C libraries (using GObject) and language bindings"
    license = "GPL, LGPL"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0")
        self.build_requires("meson/[^0.51.2]")
        self.build_requires("bison/[^3.3]")
        self.build_requires("flex/[^2.6.4]")

    def requirements(self):
        self.requires("python/[^3.7.4]")
        self.requires("glib/[^2.62.0]")

    def source(self):
        tools.get("https://github.com/GNOME/gobject-introspection/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--auto-features=disabled"]
        meson = Meson(self)
        meson.configure(source_folder="%s-%s" % (self.name, self.version), args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()

    def package_info(self):
        self.env_info.GI_TYPELIB_PATH.append(os.path.join(self.package_folder, "lib", "girepository-1.0"))
        self.env_info.PYTHONPATH = os.path.join(self.package_folder, "lib", "gobject-introspection")
