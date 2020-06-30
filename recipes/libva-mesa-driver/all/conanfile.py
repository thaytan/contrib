import os

from conans import ConanFile, Meson, tools


class LibvaMesaDriverConan(ConanFile):
    name = "libva-mesa-driver"
    license = "MIT"
    description = "VA-API user mode driver for Intel GEN Graphics family"
    settings = "os", "arch", "compiler", "build_type"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("meson/[>=0.51.2]@%s/stable" % self.user)

    def requirements(self):
        self.requires("libdrm/[>=2.4.96]@%s/stable" % self.user)
        self.requires("libva/[>=2.3.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/intel/intel-vaapi-driver/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["-Ddriverdir=" + os.path.join(self.package_folder, "lib", "dri")]
        meson = Meson(self)
        meson.configure(source_folder="intel-vaapi-driver-" + self.version, args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()

    def package_info(self):
        self.env_info.LIBVA_DRIVERS_PATH.append(os.path.join(self.package_folder, "lib", "dri"))
