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
    requires = ("gst/[^1.18]",)

    def build_requirements(self):
        if self.options.introspection:
            self.build_requires("gobject-introspection/[^1.66.1]")

    def source(self):
        git = tools.Git(folder="gst-editing-services")
        if "1.18" in self.settings.gstreamer:
            git = tools.Git(folder=self.src)
            git.clone("https://gitlab.freedesktop.org/gstreamer/gst-editing-services.git", "master")

            # Pick a random cutoff date close to HEAD on origin/master and try to build
            # https://gitlab.freedesktop.org/gstreamer/gst-editing-services/-/commit/0ec4893c8e06e80a5cc3b8f71e781de71e527163
            git.run("checkout 0ec4893c8e06e80a5cc3b8f71e781de71e527163")

            # # Build it for 1.18 by undoing some 1.19 specifics:
            # 16ef2917e24af5248dd16e96c4513d1766a1fa17 - 01 Jun, 2021 - 
            # 986d0737e4d81ffe00244092b11ce0d4a744b186 - 31 May, 2021 -
            # ec5b267249af8bbe33de1af51863b0285a9831f3 - 05 May, 2021 - undoes using gst_element_request_pad_simple
            # 7499d412135bdadeaf1cadadf180e6cc9a46e442 - Jan 15, 2021 - undoes using gst_structure_serialize,  ges: Add keyframe support to the command line formatter
            # d45e594a31dcdb788cff1d20a8f275c890eafce0 - Jan 15, 2021 - undoes using gst_caps_serialize,   command-line-formatter: Add a way to format timelines using the format
            # d7764275d819e6c419ef7eed1ea174ebd1aa041b - Jan 15, 2021 - undoes using gst_caps_serialize,   formatter: Use the new `GstEncodingProfile:element-properties` property
            # 4953fe9f45e4a92b92d1b47fcb3355694bcf6086 - Sep 08, 2020 - undoes the requirement for gst 1.19
            git.run(
                '-c user.email="cicd@civero.com" -c user.name="Chlorine Cadmium" '
                + "revert --no-edit "
                + "16ef2917e24af5248dd16e96c4513d1766a1fa17 "
                + "986d0737e4d81ffe00244092b11ce0d4a744b186 "
                + "ec5b267249af8bbe33de1af51863b0285a9831f3 "
                + "d45e594a31dcdb788cff1d20a8f275c890eafce0 "
                + "7499d412135bdadeaf1cadadf180e6cc9a46e442 "
                + "d7764275d819e6c419ef7eed1ea174ebd1aa041b "
                + "4953fe9f45e4a92b92d1b47fcb3355694bcf6086 "
            )

            self.patch("ges_launch_custom_config.patch")

        elif "1.20" in self.settings.gstreamer:
            self.get(f"https://gitlab.freedesktop.org/gstreamer/gst-editing-services/-/archive/{self.version}/gst-editing-services-{self.version}.tar.gz")

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
