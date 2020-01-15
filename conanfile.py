import os
from conans import ConanFile, Meson, tools

class LibNiceConan(ConanFile):
    name = "libnice"
    version = tools.get_env("GIT_TAG", "0.1.15")
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "An implementation of the IETF's Interactive Connectivity Establishment (ICE) standard"
    license = "LGPL"
    settings = "os", "arch", "compiler", "build_type"
    options = {"gstreamer": [True, False]}
    default_options = "gstreamer=True"
    generators = "env"

    def build_requirements(self):
        self.build_requires("meson/[>=0.51.2]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.requires("glib/[>=2.62.0]@%s/stable" % self.user)
        self.requires("openssl/[>=1.1.1b]@%s/stable" % self.user)
        if self.options.gstreamer:
            gst_version = "1.16.0"
            self.requires("gstreamer-plugins-base/[~%s]@%s/stable" % (gst_version, self.user))

    def source(self):
        tools.get("https://github.com/libnice/libnice/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--auto-features=disabled"]
        args.append(
            "-Dgstreamer=" + ("enabled" if self.options.gstreamer else "disabled")
        )
        meson = Meson(self)
        meson.configure(source_folder="%s-%s" % (self.name, self.version), args=args)
        meson.install()

    def package_info(self):
        self.env_info.GST_PLUGIN_PATH.append(
            os.path.join(self.package_folder, "lib", "gstreamer-1.0")
        )
