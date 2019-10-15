from conans import ConanFile, Meson, tools
import os


class GStreamerDevtoolsConan(ConanFile):
    name = "gstreamer-devtools"
    version = tools.get_env("GIT_TAG", "1.16.0")
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "Development and debugging tools for GStreamer"
    license = "LGPL"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"
    scm = {
        "type": "git",
        "url": "https://gitlab.com/aivero/public/gstreamer/gst-devtools-mirror",
        "revision": "rebased-155-add-psnr",
        "recursive": True,
        "subfolder": ("gst-devtools-" + version)
    }
    options = {"gtk_doc": [True, False],
               "introspection": [True, False],
               "tests": [True, False],
               "nls": [True, False]}
    default_options = "gtk_doc=False", "introspection=False", "tests=True", "nls=False"

    def build_requirements(self):
        self.build_requires("meson/[>=0.51.2]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.requires("gstreamer-plugins-base/[>=%s]@%s/stable" % (self.version, self.user))
        self.requires("gstreamer/[>=%s]@%s/stable" % (self.version, self.user))
        self.requires("json-glib/[>=1.4.4]@%s/stable" % self.user)
        self.requires("cairo/[>=1.17.2]@%s/stable" % self.user)
        self.requires("libx11/[>=1.6.8]@%s/stable" % self.user)
        self.requires("libxrender/[>=0.9.10]@%s/stable" % self.user)
        self.requires("libxext/[>=1.3.4]@%s/stable" % self.user)

    def build(self):
        meson = Meson(self)
        args = ["-Dgtk_doc=" + ("enabled" if self.options.gtk_doc else "disabled")]
        args.append("-Dintrospection=" + ("enabled" if self.options.introspection else "disabled"))
        args.append("-Dtests=" + ("enabled" if self.options.tests else "disabled"))
        args.append("-Dnls=" + ("enabled" if self.options.nls else "disabled"))
        meson.configure(source_folder="gst-devtools-" + self.version, args=args)
        meson.install()
