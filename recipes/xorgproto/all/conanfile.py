from conans import *


class XorgProtoConan(ConanFile):
    description = "combined X.Org X11 Protocol headers"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "meson/[^0.51.2]",
        "xorg-util-macros/[^1.19.1]",
    )

    def source(self):
        tools.get(f"https://xorg.freedesktop.org/archive/individual/proto/xorgproto-{self.version}.tar.bz2")

    def build(self):
        args = ["--auto-features=disabled"]
        meson = Meson(self)
        meson.configure(
            source_folder=f"{self.name}-{self.version}", args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":")\        )
        meson.install()
