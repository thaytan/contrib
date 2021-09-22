from build import *
from conans.errors import ConanInvalidConfiguration


class GstPluginsBaseRecipe(GstRecipe):
    description = "A well-groomed and well-maintained collection of GStreamer plugins and elements"
    license = "LGPL"
    options = {
        "shared": [True, False],
        "introspection": [True, False],
        "x11": [True, False],
        "audioresample": [True, False],
    }
    default_options = (
        "shared=True",
        "introspection=True",
        "x11=True",
        "audioresample=True",
    )
    build_requires = (
        "cc/[^1.0.0]",
        "meson/[>=0.55.3]",
    )
    requires = (
        "opus/[^1.3.1]",
        "pango/[^1.43.0]",
        "orc/[^0.4.29]",
        "mesa/[>=20.2.1]",
    )

    def requirements(self):
        # This will SemVer match PATH changes, but not MINOR or MAJOR changes
        # That way we can still build for a lower gst minor release (i.e. 1.18), despite a newer one being in your conan (i.e. 1.19)
        # [^1.18] will match any `1.` version - not what we need
        self.requires(f"gst/[~{self.settings.gstreamer}]")

    def validate(self):
        if str(self.settings.gstreamer) not in str(self.version):
            raise ConanInvalidConfiguration(f"GStreamer version specified in devops.yml ({self.version}) is not compatible with version specified in profile: {self.settings.gstreamer}")

    def build_requirements(self):
        if self.options.introspection:
            self.build_requires("gobject-introspection/[^1.66.1]")

    def source(self):
        if int(str(self.settings.gstreamer).split(".")[1]) == 19:
            git = tools.Git(folder=self.src)
            git.clone("https://gitlab.freedesktop.org/GStreamer/gst-plugins-base.git", f"{self.version}")

            git.run(
                '-c user.email="cicd@civero.com" -c user.name="Chlorine Cadmium" ' + "cherry-pick -x " + "4aa72cea4f99c9c47f5d88f294942b8db4a60aa0 " + "acf98372a3dbc04c23e0d3139dad1c295eedeac2 " + "ebb6b9778af00afe60bd308a27c5ddb8df932d68 "
            )

            # https://gitlab.freedesktop.org/gstreamer/gst-plugins-base/-/merge_requests/1249/commits
            # smartencoder: clean up and extend accepted formats 4aa72cea4f99c9c47f5d88f294942b8db4a60aa0
            # smartencoder: Respect user `stream-format` when specified acf98372a3dbc04c23e0d3139dad1c295eedeac2
            # encoding-profile: ignore more encoding private fields ebb6b9778af00afe60bd308a27c5ddb8df932d68
        else:
            self.get(f"https://gitlab.freedesktop.org/gstreamer/gst-plugins-base/-/archive/{self.version}/gst-plugins-base-{self.version}.tar.gz")

    def build(self):
        opts = {
            "gl_platform": "egl",
            "introspection": self.options.introspection,
            "x11": self.options.x11,
            "audioresample": self.options.audioresample,
            "gl": True,
            "videotestsrc": True,
            "audiotestsrc": True,
            "videoconvert": True,
            "app": True,
            "playback": True,
            "typefind": True,
            "orc": True,
            "opus": True,
            "pango": True,
            "videoscale": True,
            "audioconvert": True,
            "compositor": True,
            "encoding": True,
            "audiomixer": True,
            "videorate": True,
        }
        self.meson(opts)
