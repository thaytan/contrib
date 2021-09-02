from build import *
from conans.errors import ConanInvalidConfiguration


class GstPluginsGoodRecipe(GstRecipe):
    description = "Plug-ins is a set of plugins that we consider to have good quality code and correct functionality"
    license = "LGPL"
    # If set to true, select version highest semver matching version from devops.yml
    gst_match_version = True
    settings = GstRecipe.settings + ("hardware",)
    exports = "*.patch"
    options = {
        "aivero_rvl_matroska": [True, False],
        "autodetect": [True, False],
        "isomp4": [True, False],
        "jpeg": [True, False],
        "matroska": [True, False],
        "multifile": [True, False],
        "png": [True, False],
        "rtp": [True, False],
        "rtsp": [True, False],
        "udp": [True, False],
        "videofilter": [True, False],
        "videomixer": [True, False],
        "vpx": [True, False],
        "ximagesrc_xdamage": [True, False],
        "ximagesrc_xshm": [True, False],
        "ximagesrc": [True, False],
        "v4l2": [True, False],
    }
    default_options = (
        "aivero_rvl_matroska=True",
        "autodetect=True",
        "isomp4=True",
        "jpeg=True",
        "matroska=True",
        "multifile=True",
        "png=True",
        "rtp=True",
        "rtsp=True",
        "udp=True",
        "videofilter=True",
        "videomixer=True",
        "vpx=True",
        "ximagesrc_xdamage=False",
        "ximagesrc_xshm=True",
        "ximagesrc=True",
        "v4l2=False",
    )

    build_requires = (
        "cc/[^1.0.0]",
        "meson/[>=0.57.2]",
        "git/[^2.30.0]",
    )

    def validate(self):
        if str(self.settings.gstreamer) not in str(self.version):
            raise ConanInvalidConfiguration(f"GStreamer version specified in devops.yml ({self.version}) is not compatible with version specified in profile: {self.settings.gstreamer}")

    def configure(self):
        if self.settings.hardware == "rpi":
            if self.settings.arch == "armv8":
                # enable v4l2 for rpi 64-bit
                self.options.v4l2 = True

    def requirements(self):
        # This will SemVer match PATH changes, but not MINOR or MAJOR changes
        # That way we can still build for a lower gst minor release (i.e. 1.18), despite a newer one being in your conan (i.e. 1.19)
        # [^1.18] will match any `1.` version - not what we need
        self.requires(f"gst-plugins-base/[~{self.settings.gstreamer}]")

        # gst-plugins-bad -> pango -> freetype -> png
        # if self.options.png:
        #     self.requires("libpng/[^1.6.37]")
        if self.options.vpx:
            self.requires("libvpx/[^1.8.0]")
        if self.options.jpeg:
            self.requires("libjpeg-turbo/[^2.0.3]")

    def source(self):
        if "1.18" in self.settings.gstreamer:
            git = tools.Git(folder=f"{self.name}-{self.version}.src")
            git.clone("https://gitlab.freedesktop.org/GStreamer/gst-plugins-good.git", self.version)

            # Apply MR: https://gitlab.freedesktop.org/gstreamer/gst-plugins-good/-/merge_requests/707/commits
            ## Apply: vp9enc: expose row-mt property https://gitlab.freedesktop.org/gstreamer/gst-plugins-good/-/commit/39fcc7f58fa258ae8bc2836bc7804434d1afae5a
            ## Apply: vpxenc: change default for deadline to good quality https://gitlab.freedesktop.org/gstreamer/gst-plugins-good/-/commit/fe6b59d0ccf05fd19cc2dc2273769aee384c7046
            ## Apply: vp9enc: expose tile-columns and tile-rows properties  https://gitlab.freedesktop.org/gstreamer/gst-plugins-good/-/commit/13cf3fe2a698280bc8ae698ed60a87ebe992170a
            ## Apply: vpxenc: add configure_encoder virtual method https://gitlab.freedesktop.org/gstreamer/gst-plugins-good/-/commit/e61932c3588993e68753b5bd3b1ff58794576cd8

            git.run(
                '-c user.email="cicd@civero.com" -c user.name="Chlorine Cadmium" '
                + "cherry-pick -x "
                + "e61932c3588993e68753b5bd3b1ff58794576cd8 "
                + "13cf3fe2a698280bc8ae698ed60a87ebe992170a "
                + "fe6b59d0ccf05fd19cc2dc2273769aee384c7046 "
                + "39fcc7f58fa258ae8bc2836bc7804434d1afae5a "
                + "d270fa498c49a6a1a2454e7f984247d735ee179b "
            )

            #  matroskamux: Always write a tags element into seekhead https://gitlab.freedesktop.org/gstreamer/gst-plugins-good/-/commit/d270fa498c49a6a1a2454e7f984247d735ee179b
            # self.patch("always-write-tags-to-seekhead.patch")
            # self.patch("gst-tags-in-mkv.patch")
            git.run('-c user.email="cicd@civero.com" -c user.name="Chlorine Cadmium" am -3 ../0001-matroska-Support-any-tag.patch')

        elif int(str(self.settings.gstreamer).split(".")[1]) == 19:
            git = tools.Git(folder=f"{self.name}-{self.version}.src")
            git.clone("https://gitlab.freedesktop.org/GStreamer/gst-plugins-good.git", self.version)

            # Build current 1.19 tag and apply
            #  matroskamux: Always write a tags element into seekhead https://gitlab.freedesktop.org/gstreamer/gst-plugins-good/-/commit/d270fa498c49a6a1a2454e7f984247d735ee179b

            # https://gitlab.freedesktop.org/gstreamer/gst-plugins-good/-/merge_requests/1047
            # matroska-mux: support H264 avc3 / H265 hev1 9bd8d608d5bae27ec5ff09e733f76ca32b17420c
            ## isomp4/qtmux: allow renegotiating when tier / level / profile change cb75eda13b20b5633546e40e7d8fcc0d479ee901
            ## isomp4/qtmux: accept video/x-h264, stream-format=avc3 896c49cf4959815badcb5dd538a5d522a1f1629e
            ## isomp4/qtmux: make sure to switch to next chunk on new caps fa835d686f7edbaf9617f496a9fee3132577df42
            ## isomp4/atoms: fix multiple stsd entries e069824c7de530f8095fedce0820e846c72d466b

            # qtmux: Don't need to update track per GstCaps if it's not changed adae01e4c3bf6c091e9ddd5f44f03a0d7d4fe6eb
            git.run(
                '-c user.email="cicd@civero.com" -c user.name="Chlorine Cadmium" '
                + "cherry-pick -x "
                + "d270fa498c49a6a1a2454e7f984247d735ee179b "
                + "adae01e4c3bf6c091e9ddd5f44f03a0d7d4fe6eb "
                + "e069824c7de530f8095fedce0820e846c72d466b "
                + "fa835d686f7edbaf9617f496a9fee3132577df42 "
                + "896c49cf4959815badcb5dd538a5d522a1f1629e "
                + "cb75eda13b20b5633546e40e7d8fcc0d479ee901 "
                + "9bd8d608d5bae27ec5ff09e733f76ca32b17420c "
            )
            git.run('-c user.email="cicd@civero.com" -c user.name="Chlorine Cadmium" am -3 ../0001-matroska-Support-any-tag.patch')

        elif int(str(self.settings.gstreamer).split(".")[1]) > 19:
            self.get(f"https://gitlab.freedesktop.org/gstreamer/gst-plugins-good/-/archive/{self.version}/gst-plugins-good-{self.version}.tar.gz")
        else:
            raise (f"GStreamer version {self.settings.gstreamer} not supported")

        # Add our own custom changes
        if self.options.aivero_rvl_matroska:
            git.run('-c user.email="cicd@civero.com" -c user.name="Chlorine Cadmium" am -3 ../0001-matroska-add-support-for-custom-video-rvl-depth-map-.patch')

    def build(self):
        opts = {
            "autodetect": True,
            "isomp4": True,
            "jpeg": True,
            "matroska": True,
            "multifile": True,
            "png": True,
            "rtp": True,
            "rtpmanager": True,
            "rtsp": True,
            "udp": True,
            "videofilter": True,
            "videomixer": True,
            "vpx": True,
            "ximagesrc-xdamage": True,
            "ximagesrc": True,
        }
        opts["v4l2"] = self.options.v4l2
        self.meson(opts)
