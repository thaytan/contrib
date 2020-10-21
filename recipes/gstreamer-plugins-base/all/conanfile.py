import os
from conans import *


class GStreamerPluginsBaseConan(ConanFile):
    description = "A well-groomed and well-maintained collection of GStreamer plugins and elements"
    license = "LGPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build", "gstreamer"
    options = {
        "audioresample": [True, False],
    }
    default_options = ("audioresample=False",)
    build_requires = (
        "cc/[^1.0.0]",
        "meson/[^0.55.2]",
        "mesa/[^20.2.1]",
        "gobject-introspection/[^1.59.3]",
        "opus/[^1.3.1]",
        "pango/[^1.43.0]",
        "libx11/[^1.6.8]",
    )
    requires = ("orc/[^0.4.29]",)

    def requirements(self):
        self.requires(f"gstreamer/[~{self.settings.gstreamer}]")

    def source(self):
        tools.get(f"https://github.com/GStreamer/gst-plugins-base/archive/{self.version}.tar.gz")

    def build(self):
        args = [
            "--auto-features=disabled",
            "-Dgl_platform=egl",
            "-Dintrospection=enabled",
            "-Dgl=enabled",
            "-Dx11=enabled",
            "-Dvideotestsrc=enabled",
            "-Daudiotestsrc=enabled",
            "-Dvideoconvert=enabled",
            "-Dapp=enabled",
            "-Dplayback=enabled",
            "-Dtypefind=enabled",
            "-Dorc=enabled",
            "-Dopus=enabled",
            "-Dpango=enabled",
            "-Dvideoscale=enabled",
            "-Daudioconvert=enabled",
        ]
        args.append("-Daudioresample=" + ("enabled" if self.options.audioresample else "disabled"))
        meson = Meson(self)
        meson.configure(args, source_folder=f"gst-plugins-base-{self.version}", pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()
