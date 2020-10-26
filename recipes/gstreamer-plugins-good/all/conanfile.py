from build import *


class GStreamerPluginsGoodRecipe(Recipe):
    description = "Plug-ins is a set of plugins that we consider to have good quality code and correct functionality"
    license = "LGPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build", "gstreamer"
    options = {"x11": [True, False]}
    default_options = ("x11=True",)
    build_requires = ("meson/[^0.55.3]",)
    requires = (
        "libpng/[^1.6.37]",
        "libvpx/[^1.8.0]",
        "libjpeg-turbo/[^2.0.3]",
    )

    def requirements(self):
        self.requires(f"gstreamer-plugins-base/[~{self.settings.gstreamer}]")
        if self.options.x11:
            self.requires("libxdamage/[^1.1.5]")

    def source(self):
        self.get(f"https://github.com/GStreamer/gst-plugins-good/archive/{self.version}.tar.gz")

    def build(self):
        args = [
            "--auto-features=disabled",
            "-Dautodetect=enabled",
            "-Drtp=enabled",
            "-Drtsp=enabled",
            "-Drtpmanager=enabled",
            "-Dudp=enabled",
            "-Dpng=enabled",
            "-Disomp4=enabled",
            "-Dvideofilter=enabled",
            "-Dvpx=enabled",
            "-Dmultifile=enabled",
            "-Dmatroska=enabled",
            "-Dvideomixer=enabled",
            "-Dximagesrc=enabled",
            "-Dximagesrc-xdamage=enabled",
            "-Dxshm=enabled",
            "-Djpeg=enabled",
        ]
        self.meson(args)
