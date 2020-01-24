import os

from conans import ConanFile, Meson, tools


class GStreamerRtspServerConan(ConanFile):
    name = "gstreamer-rtsp-server"
    version = tools.get_env("GIT_TAG", "1.16.2")
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "A framework for streaming media"
    license = "LGPL"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "examples": [True, False],
        "tests": [True, False],
        "introspection": [True, False],
        "rtspclientsink": [True, False],
    }
    default_options = ("examples=False", "tests=False", "introspection=True", "rtspclientsink=True")
    generators = "env"

    def build_requirements(self):
        self.build_requires("env-generator/1.0.0@%s/stable" % self.user)
        self.build_requires("meson/[>=0.51.2]@%s/stable" % self.user)
        self.build_requires("bison/[>=3.3]@%s/stable" % self.user)
        self.build_requires("flex/[>=2.6.4]@%s/stable" % self.user)
        if self.options.introspection:
            self.build_requires("gobject-introspection/[>=1.59.3]@%s/stable" % self.user)

    def requirements(self):
        self.requires("glib/[>=2.62.0]@%s/stable" % self.user)
        self.requires("gstreamer/%s@%s/stable" % (self.version, self.user))
        self.requires("gstreamer-plugins-base/%s@%s/stable" % (self.version, self.user))

    def source(self):
        tools.get("https://gitlab.freedesktop.org/gstreamer/gst-rtsp-server/-/archive/%s/gst-rtsp-server-%s.tar.gz" % (self.version, self.version))

    def build(self):
        args = ["--auto-features=disabled"]
        args.append("-Dcheck=" + ("enabled" if self.options.examples else "disabled"))
        args.append("-Dtools=" + ("enabled" if self.options.tests else "disabled"))
        args.append("-Dintrospection=" + ("enabled" if self.options.introspection else "disabled"))
        args.append("-Drtspclientsink=" + ("enabled" if self.options.rtspclientsink else "disabled"))
        meson = Meson(self)
        meson.configure(source_folder="gst-rtsp-server-%s" % self.version, args=args)
        meson.install()

    def package_info(self):
        self.env_info.GST_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
        self.env_info.GI_TYPELIB_PATH.append(os.path.join(self.package_folder, "lib", "girepository-1.0"))
