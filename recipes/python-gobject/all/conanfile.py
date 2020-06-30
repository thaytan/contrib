import os

from conans import ConanFile, Meson, tools


class PythonGobjectConan(ConanFile):
    name = "python-gobject"
    description = "Python GObject bindings"
    license = "LGPL"
    settings = "os", "arch", "compiler", "build_type"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("meson/[>=0.51.2]@%s/stable" % self.user)

    def requirements(self):
        self.requires("gobject-introspection/[>=1.59.3]@%s/stable" % self.user)
        self.requires("python-cairo/[>=1.18.2]@%s/stable" % self.user)

    def source(self):
        tools.get("https://gitlab.gnome.org/GNOME/pygobject/-/archive/{0}/pygobject-{0}.tar.gz".format(self.version))

    def build(self):
        args = ["--auto-features=disabled", "--wrap-mode=nofallback"]
        meson = Meson(self)
        meson.configure(source_folder="pygobject-" + self.version, args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()

    def package_info(self):
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "lib", "python3.7", "site-packages"))
