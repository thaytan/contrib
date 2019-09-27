from conans import ConanFile, Meson, tools
import os

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "1.59.3"
    except:
        return None

class GObjectIntrospectionConan(ConanFile):
    name = "gobject-introspection"
    version = get_version()
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "Middleware layer between C libraries (using GObject) and language bindings"
    license = "GPL, LGPL"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def build_requirements(self):
        self.build_requires("meson/[>=0.51.2]@%s/stable" % self.user)
        self.build_requires("bison/[>=3.3]@%s/stable" % self.user)
        self.build_requires("flex/[>=2.6.4]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.requires("glib/[>=2.62.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/GNOME/gobject-introspection/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--auto-features=disabled"]
        meson = Meson(self)
        meson.configure(source_folder="%s-%s" % (self.name,  self.version), args=args)
        meson.install()

    def package_info(self):
        self.env_info.XDG_DATA_DIRS.append(os.path.join(self.package_folder, "share"))
        self.env_info.GI_TYPELIB_PATH.append(os.path.join(self.package_folder, "lib", "girepository-1.0"))
