import os

from conans import ConanFile, Meson, tools

class GStreamerVaapiConan(ConanFile):
    name = "gstreamer-vaapi"
    description = "Hardware-accelerated video decoding, encoding and processing on Intel graphics through VA-API"
    license = "LGPL"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "introspection": [True, False],
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

    def set_version(self):
        git = tools.Git(folder=self.recipe_folder)
        tag, branch = git.get_tag(), git.get_branch()
        self.version = tag if tag and branch.startswith("HEAD") else branch

    def build_requirements(self):
        self.requires("generators/[>=1.0.0]@%s/stable" % self.user)
        self.build_requires("meson/[>=0.51.2]@%s/stable" % self.user)
        if self.options.introspection:
            self.build_requires("gobject-introspection/[>=1.59.3]@%s/stable" % self.user)

    def requirements(self):
        gst_version = "master" if self.version == "master" else "[~%s]" % self.version
        gst_channel = "testing" if self.version == "master" else "stable"
        self.requires("gstreamer-plugins-base/%s@%s/%s" % (gst_version, self.user, gst_channel))
        self.requires("gstreamer-plugins-bad/%s@%s/%s" % (gst_version, self.user, gst_channel))
        self.requires("libva/[>=2.3.0]@%s/stable" % self.user)

    def source(self):
        git = tools.Git(folder="gstreamer-vaapi-" + self.version)
        git.clone(url="https://gitlab.freedesktop.org/gstreamer/gstreamer-vaapi.git", branch=self.version, shallow=True)

    def build(self):
        args = ["--auto-features=disabled"]
        args.append("-Dwith_encoders=" + ("yes" if self.options.encoders else "no"))
        meson = Meson(self)
        meson.configure(source_folder="gstreamer-vaapi-" + self.version, args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()
        

    def package_info(self):
        self.env_info.GST_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
