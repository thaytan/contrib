import os

from conans import ConanFile, Meson, tools


class GStreamerConan(ConanFile):
    name = "gstreamer"
    version = tools.get_env("GIT_TAG", "master")
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "A framework for streaming media"
    license = "LGPL"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "introspection": [True, False],
        "check": [True, False],
        "tools": [True, False],
    }
    default_options = (
        "introspection=True",
        "check=True",
        "tools=True",
    )
    generators = "env"

    def build_requirements(self):
        self.build_requires("env-generator/1.0.0@%s/stable" % self.user)
        self.build_requires("meson/[>=0.51.2]@%s/stable" % self.user)
        self.build_requires("bison/[>=3.3]@%s/stable" % self.user)
        self.build_requires("flex/[>=2.6.4]@%s/stable" % self.user)
        if self.options.introspection:
            self.build_requires("gobject-introspection/[>=1.59.3]@%s/stable" % self.user, )

    def requirements(self):
        self.requires("glib/[>=2.62.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/GStreamer/gstreamer/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--auto-features=disabled"]
        args.append("-Dintrospection=" + ("enabled" if self.options.introspection else "disabled"))
        args.append("-Dcheck=" + ("enabled" if self.options.check else "disabled"))
        args.append("-Dtools=" + ("enabled" if self.options.tools else "disabled"))
        meson = Meson(self)
        meson.configure(source_folder="%s-%s" % (self.name, self.version), args=args)
        meson.install()

    def package_info(self):
        self.env_info.GST_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
        self.env_info.GST_PLUGIN_SCANNER = os.path.join(self.package_folder, "bin", "gstreamer-1.0", "gst-plugin-scanner")
        self.env_info.GI_TYPELIB_PATH.append(os.path.join(self.package_folder, "lib", "girepository-1.0"))
