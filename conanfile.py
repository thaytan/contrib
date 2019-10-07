import os

from conans import ConanFile, Meson, tools


def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "3.33.1"
    except:
        return None

class PythonGobjectConan(ConanFile):
    name = "python-gobject"
    version = get_version()
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "Python GObject bindings"
    license = "LGPL"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def build_requirements(self):
        self.build_requires("gobject-introspection/[>=1.59.3]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.requires("gobject-introspection/[>=1.59.3]@%s/stable" % self.user)
        self.requires("cairo/[>=1.17.2]@%s/stable" % self.user)

    def source(self):
        tools.get("https://gitlab.gnome.org/GNOME/pygobject/-/archive/{0}/pygobject-{0}.tar.gz".format(self.version))

    def build(self):
        args = ["--auto-features=disabled"]
        meson = Meson(self)
        meson.configure(source_folder="pygobject-" + self.version, args=args)
        meson.install()

    def package_info(self):
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "lib", "python3.6", "site-packages"))
