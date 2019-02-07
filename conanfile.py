from conans import ConanFile, Meson, tools
import os

class GObjectIntrospectionConan(ConanFile):
    name = "gobject-introspection"
    version = "1.59.3"
    default_user = "bincrafters"
    url = "https://github.com/prozum/conan-gobject-introspection"
    description = "A framework for streaming media"
    license = "https://github.com/GNOME/gobject-introspection/blob/master/COPYING"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"

    def requirements(self):
        self.requires("glib/2.58.1@%s/stable" % self.user)
        self.requires("libffi/3.3-rc0@%s/stable" % self.user, private=True)
        self.requires("bison/3.0.4@%s/stable" % self.user, private=True)
        self.requires("flex/2.6.4@%s/stable" % self.user, private=True)

    def source(self):
        tools.get("https://github.com/GNOME/gobject-introspection/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--libdir=lib", "--auto-features=disabled"]
        meson = Meson(self)
        meson.configure(source_folder="gobject-introspection-" + self.version, args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.build()
        meson.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.PKG_CONFIG_PATH.append(os.path.join(self.package_folder, "lib", "pkgconfig"))
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
