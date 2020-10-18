import os

from conans import *


class IntelVaapiDriverConan(ConanFile):
    description = "VA-API user mode driver for Intel GEN Graphics family"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    options = {"x11": [True, False], "wayland": [True, False]}
    default_options = ("x11=True", "wayland=False")
    build_requires = (
        "meson/[^0.51.2]",
    )
    requires = (
        "base/[^1.0.0]",
        "libdrm/[^2.4.96]",
        "libva/[^2.3.0]",
    )

    def source(self):
        tools.get(f"https://github.com/intel/intel-vaapi-driver/archive/{self.version}.tar.gz")

    def build(self):
        args = ["--auto-features=disabled"]
        args.append("-Dwith_x11=" + ("yes" if self.options.x11 else "no"))
        args.append("-Dwith_wayland=" + ("yes" if self.options.wayland else "no"))
        args.append("-Ddriverdir=" + os.path.join(self.package_folder, "lib", "dri"))
        meson = Meson(self)
        meson.configure(source_folder=f"{self.name, self.version), args=args}-{pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"}")
        meson.install()

    def package_info(self):
        self.env_info.LIBVA_DRIVERS_PATH.append(os.path.join(self.package_folder, "lib", "dri"))
