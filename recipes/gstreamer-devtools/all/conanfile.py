import os

from conans import ConanFile, Meson, tools

def get_version():
    git = tools.Git()
    try:
        tag, branch = git.get_tag(), git.get_branch()
        return tag if tag and branch.startswith("HEAD") else branch
    except:
        return None


class GStreamerDevtoolsConan(ConanFile):
    name = "gstreamer-devtools"
    version = get_version()
    gst_version = "[~1]"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "Development and debugging tools for GStreamer"
    license = "LGPL"
    settings = "os", "arch", "compiler", "build_type"

    options = {"gtk_doc": [True, False], "introspection": [True, False], "tests": [True, False], "nls": [True, False]}
    default_options = "gtk_doc=False", "introspection=False", "tests=True", "nls=False"

    def build_requirements(self):
        self.build_requires("generators/[>=1.0.0]@%s/stable" % self.user)
        self.build_requires("meson/[>=0.51.2]@%s/stable" % self.user)

    def source(self):
        git = tools.Git(folder="gst-devtools")
        git.clone("https://gitlab.com/aivero/public/gstreamer/gst-devtools-mirror.git", "rebased-aivero_mse_compare_changes")

    def requirements(self):
        self.requires(
            "gstreamer-plugins-base/%s@%s/stable" % (self.gst_version, self.user)
        )
        self.requires("json-glib/[~1.4.4]@%s/stable" % self.user)

    def build(self):
        args = ["--auto-features=disabled"]
        meson = Meson(self)
        meson.configure(source_folder="gst-devtools", args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()
