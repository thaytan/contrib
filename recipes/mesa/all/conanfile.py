import os

from conans import *


class MesaConan(ConanFile):
    description = "An open-source implementation of the OpenGL specification"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    options = {"x11": [True, False]}
    default_options = ("x11=True",)
    build_requires = (
        "meson/[^0.51.2]",
        "gettext/[^0.20.1]",
        "bison/[^3.3]",
        "flex/[^2.6.4]",
        "python-mako/[^1.1.0]",
        "zlib/[^1.2.11]",
        "expat/[^2.2.7]",
        "libdrm/[^2.4.99]",
        if self.options.x11:
            self.build_requires("libx11/[^1.6.8]")
            self.build_requires("libxext/[^1.3.4]")
            self.build_requires("libxdamage/[^1.1.5]")
            self.build_requires("libxshmfence/[^1.3]")
            self.build_requires("libxxf86vm/[^1.1.4]")
    )
    requires = (
        "base/[^1.0.0]",
        "libglvnd/[^1.2.0]",
    )

    def source(self):
        tools.get(f"https://mesa.freedesktop.org/archive/mesa-{self.version}.tar.xz")

    def build(self):
        args = [
            "--auto-features=disabled",
            "--wrap-mode=nofallback",
            "-Dglvnd=true",
            "-Dglx=dri",
            "-Degl=true",
            "-Dgles1=false",
            "-Dgles2=true",
            "-Dgles3=true",
            "-Dplatforms=x11",
            "-Dvulkan-drivers=",
            "-Dgallium-drivers=",
        ]
        if self.settings.arch_build == "x86_64":
            args.append("-Ddri-drivers=i915,i965")
        if self.settings.arch_build == "armv8":
            args.append("-Dgallium-drivers=nouveau,tegra")
        meson = Meson(self)
        meson.configure(source_folder=f"{self.name, self.version), args=args}-{pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"}")
        meson.install()

    def package_info(self):
        self.env_info.LIBGL_DRIVERS_PATH.append(os.path.join(self.package_folder, "lib", "dri"))
