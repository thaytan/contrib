import os

from conans import ConanFile, Meson, tools


class Gtk3Conan(ConanFile):
    name = "gtk3"
    version = tools.get_env("GIT_TAG", "3.24.11")
    description = "GObject-based multi-platform GUI toolkit"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "LGPL-2.1"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "introspection": [True, False],
        "x11": [True, False],
    }
    default_options = (
        "introspection=True",
        "x11=True",
    )
    generators ="pkgconf"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("meson/[>=0.51.2]@%s/stable" % self.user)
        self.build_requires("gettext/[>=0.20.1]@%s/stable" % self.user)
        if self.options.introspection:
            self.build_requires("gobject-introspection/[>=1.59.3]@%s/stable" % self.user, )

    def requirements(self):
        self.requires("glib/[>=2.62.0]@%s/stable" % self.user)
        self.requires("cairo/[>=1.16.0]@%s/stable" % self.user)
        self.requires("libepoxy/[>=1.5.3]@%s/stable" % self.user)
        self.requires("atk/[>=2.35.1]@%s/stable" % self.user)
        self.requires("at-spi2-atk/[>=2.34.0]@%s/stable" % self.user)
        self.requires("gdk-pixbuf/[>=2.38.2]@%s/stable" % self.user)
        self.requires("pango/[>=1.43.0]@%s/stable" % self.user)
        if self.options.x11:
            self.requires("libx11/[>=1.6.8]@%s/stable" % self.user)
            self.requires("libxkbcommon/[>=0.8.4]@%s/stable" % self.user)
            self.requires("libxrandr/[>=1.5.2]@%s/stable" % self.user)
            self.requires("libxi/[>=1.7.1]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/GNOME/gtk/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--auto-features=disabled", "--wrap-mode=nofallback", "-Dwayland_backend=false"]
        meson = Meson(self)
        meson.configure(source_folder="gtk-" + self.version, args=args)
        meson.install()

    def package_info(self):
        self.env_info.GI_TYPELIB_PATH.append(os.path.join(self.package_folder, "lib", "girepository-1.0"))
