from build import *


class IntelVaapiDriver(Recipe):
    description = "VA-API user mode driver for Intel GEN Graphics family"
    license = "MIT"
    options = {"x11": [True, False], "wayland": [True, False]}
    default_options = ("x11=True", "wayland=False")
    build_requires = (
        "cc/[^1.0.0]",
        "meson/[>=0.51.2]",
    )
    requires = (
        "libva/[^2.3.0]",
    )

    def source(self):
        self.get(f"https://github.com/intel/intel-vaapi-driver/archive/{self.version}.tar.gz")

    def build(self):
        opts = {}
        opts["with_x11"] = self.options.x11
        opts["with_wayland"] = self.options.wayland
        opts["driverdir"] = os.path.join(self.package_folder, "lib", "dri")
        self.meson(opts)

    def package_info(self):
        self.env_info.LIBVA_DRIVERS_PATH.append(os.path.join(self.package_folder, "lib", "dri"))
