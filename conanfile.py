import os
from os import environ, path, pathsep

from conans import ConanFile, Meson, tools


class GdkPixbufConan(ConanFile):
    name = "gdk-pixbuf"
    version = tools.get_env("GIT_TAG", "2.38.2")
    description = "An image loading library"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "LGPL-2.1"
    settings = "os", "arch", "compiler", "build_type"
    generators ="pkgconf"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("meson/[>=0.51.2]@%s/stable" % self.user)
        self.build_requires("gobject-introspection/[>=1.59.3]@%s/stable" % self.user)
        self.build_requires("gettext/[>=0.20.1]@%s/stable" % self.user)

    def requirements(self):
        self.requires("glib/[>=2.62.0]@%s/stable" % self.user)
        self.requires("libx11/[>=1.6.8]@%s/stable" % self.user)
        self.requires("libpng/[>=1.6.37]@%s/stable" % self.user)
        self.requires("shared-mime-info/[>=1.14]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/GNOME/gdk-pixbuf/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--auto-features=disabled", "--wrap-mode=nofallback", "-Dinstalled_tests=false", "-Drelocatable=true"]
        with tools.environment_append({"PATH": environ["PATH"] + pathsep + path.join(self.build_folder, "gdk-pixbuf")}):
            meson = Meson(self)
            meson.configure(source_folder="%s-%s" % (self.name, self.version), args=args)
            meson.install()

    def package_info(self):
        self.env_info.GI_TYPELIB_PATH.append(os.path.join(self.package_folder, "lib", "girepository-1.0"))
