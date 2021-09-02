from build import *


class GstEditingServicesRecipe(GstRecipe):
    description = " This is a high-level library for facilitating the creation of audio/video non-linear editors."
    license = "LGPL"
    exports = "*.patch"
    options = {
        "doc": [True, False],
        "examples": [True, False],
        "introspection": [True, False],
        "tests": [True, False],
        "tools": [True, False],
        "bash_completion": [True, False],
        "pygi_overrides_dir": [True, False],
        "xptv": [True, False],
        "python": [True, False],
        "libpython_dir": [True, False],
        "validate": [True, False],
    }
    default_options = (
        "doc=False",
        "examples=False",
        "introspection=True",
        "tests=False",
        "tools=False",
        "bash_completion=False",
        "pygi_overrides_dir=False",
        "xptv=False",
        "python=False",
        "libpython_dir=False",
        "validate=False",
    )
    build_requires = (
        "cc/[^1.0.0]",
        "meson/[>=0.55.3]",
        "flex/[^2.6.4]",
    )

    def requirements(self):
        # This will SemVer match PATH changes, but not MINOR or MAJOR changes
        # That way we can still build for a lower gst minor release (i.e. 1.18), despite a newer one being in your conan (i.e. 1.19)
        # [^1.18] will match any `1.` version - not what we need
        self.requires(f"gst-plugins-base/[~{self.settings.gstreamer}]")

    def build_requirements(self):
        if self.options.introspection:
            self.build_requires("gobject-introspection/[^1.66.1]")

    def source(self):
        git = tools.Git(folder="gst-editing-services")
        if int(str(self.settings.gstreamer).split(".")[1]) == 19:
            git = tools.Git(folder=self.src)
            git.clone("https://gitlab.freedesktop.org/gstreamer/gst-editing-services.git", "master")

            # Pick a HEAD on 2/Sept/2021: 
            # https://gitlab.freedesktop.org/gstreamer/gst-editing-services/-/commit/0ec4893c8e06e80a5cc3b8f71e781de71e527163
            git.run("checkout 0ec4893c8e06e80a5cc3b8f71e781de71e527163")

            self.patch("ges_launch_custom_config.patch")

        elif int(str(self.settings.gstreamer).split(".")[1]) > 19:
            self.get(f"https://gitlab.freedesktop.org/gstreamer/gst-editing-services/-/archive/{self.version}/gst-editing-services-{self.version}.tar.gz")
        else:
            raise (f"GStreamer version {self.settings.gstreamer} not supported")

    def build(self):
        opts = {
            "doc": self.options.doc,
            "examples": self.options.examples,
            "introspection": self.options.introspection,
            "tests": self.options.tests,
            "tools": self.options.tools,
            "bash-completion": self.options.bash_completion,
            "pygi-overrides-dir": self.options.pygi_overrides_dir,
            "xptv": self.options.xptv,
            "python": self.options.python,
            "libpython-dir": self.options.libpython_dir,
            # TODO: take this from options!!!
            "validate": False,
        }
        self.meson(opts)
