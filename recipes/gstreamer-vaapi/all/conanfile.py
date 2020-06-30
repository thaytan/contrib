import os

from conans import ConanFile, Meson, tools


class GStreamerVaapiConan(ConanFile):
    description = "Hardware-accelerated video decoding, encoding and processing on Intel graphics through VA-API"
    license = "LGPL"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    options = {
        "introspection": [True, False]
        "encoders": [True, False],
        "egl": [True, False],
        "x11": [True, False],
        "drm": [True, False],
        "glx": [True, False],
    }
    default_options = (
        "introspection=True",
        "encoders=True",
        "egl=True",
        "x11=True",
        "drm=True",
        "glx=True",
    )

    def build_requirements(self):
        self.requires("generators/[>=1.0.0]@%s/stable" % self.user)
        self.build_requires("meson/[>=0.51.2]@%s/stable" % self.user)
        if self.options.introspection:
            self.build_requires("gobject-introspection/[>=1.59.3]@%s/stable" % self.user)

    def requirements(self):
        self.requires("gstreamer-plugins-base/[~%s]@%s/stable" % (self.version, self.user))
        self.requires("gstreamer-plugins-bad/[~%s]@%s/stable" % (self.version, self.user))
        self.requires("libva/[>=2.3.0]@%s/stable" % self.user)

    def source(self):
        git = tools.Git(folder="gstreamer-vaapi-" + self.version)
        git.clone(
            url="https://gitlab.freedesktop.org/gstreamer/gstreamer-vaapi.git", branch=self.version, shallow=True
        )

    def build(self):
        args = ["--auto-features=disabled"]
        args.append("-Dwith_encoders=" + ("yes" if self.options.encoders else "no"))
        meson = Meson(self)
        meson.configure(source_folder="gstreamer-vaapi-" + self.version, args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()
