from conans import ConanFile, Meson, tools
import os

class GObjectIntrospectionConan(ConanFile):
    name = "gobject-introspection"
    version = "1.59.3"
    default_user = "bincrafters"
    default_channel = "stable"
    url = "https://github.com/prozum/conan-gobject-introspection"
    description = "A framework for streaming media"
    license = "https://github.com/GNOME/gobject-introspection/blob/master/COPYING"
    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False]}
    default_options = "fPIC=True"

    def requirements(self):
        self.requires("glib/2.58.1@%s/%s" % (self.user, self.channel))

    def build_requirements(self):
        self.build_requires("bison/3.0.4@%s/%s" % (self.user, self.channel))
        self.build_requires("flex/2.6.4@%s/%s" % (self.user, self.channel))

    def source(self):
        tools.get("https://github.com/GNOME/gobject-introspection/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--auto-features=disabled"]
        meson = Meson(self)
        meson.configure(source_folder="gobject-introspection-" + self.version, args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.build()
        meson.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        for file in os.listdir(os.path.join(self.package_folder, "lib", "pkgconfig")):
            setattr(self.env_info, "PKG_CONFIG_%s_PREFIX" % file[:-3].replace(".", "_").replace("-", "_").upper(), self.package_folder)
        self.env_info.PKG_CONFIG_PATH.append(os.path.join(self.package_folder, "lib", "pkgconfig"))
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.XDG_DATA_DIRS.append(os.path.join(self.package_folder, "share"))
