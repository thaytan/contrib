from build import *


class LibvaMesaDriverRecipe(Recipe):
    description = "VA-API user mode driver for Intel GEN Graphics family"
    license = "MIT"
    build_requires = ("cc/[^1.0.0]", "meson/[^0.51.2]")
    requires = (
        "libdrm/[^2.4.96]",
        "libva/[^2.3.0]",
    )

    def source(self):
        self.get(f"https://github.com/intel/intel-vaapi-driver/archive/{self.version}.tar.gz")

    def build(self):
        args = [
            f"-Ddriverdir={os.path.join(self.package_folder, 'lib', 'dri')}",
        ]
        self.meson(args)

    def package_info(self):
        self.env_info.LIBVA_DRIVERS_PATH.append(os.path.join(self.package_folder, "lib", "dri"))
