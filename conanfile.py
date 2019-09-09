from conans import ConanFile, Meson, tools
import os

class GObjectIntrospectionConan(ConanFile):
    name = "gobject-introspection"
    version = "1.59.3"
    url = "https://gitlab.com/aivero/public/conan/conan-gobject-introspection"
    description = "Middleware layer between C libraries (using GObject) and language bindings"
    license = "https://github.com/GNOME/gobject-introspection/blob/master/COPYING"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/%s" % (self.user, self.channel))
        self.requires("glib/2.58.1@%s/%s" % (self.user, self.channel))
        self.requires("bison/3.3@%s/%s" % (self.user, self.channel), private=True)
        self.requires("flex/2.6.4@%s/%s" % (self.user, self.channel), private=True)

    def source(self):
        tools.get("https://github.com/GNOME/gobject-introspection/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--auto-features=disabled"]
        meson = Meson(self)
        meson.configure(source_folder="%s-%s" % (self.name,  self.version), args=args)
        meson.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.XDG_DATA_DIRS.append(os.path.join(self.package_folder, "share"))
        self.env_info.GI_TYPELIB_PATH.append(os.path.join(self.package_folder, "lib", "girepository-1.0"))
