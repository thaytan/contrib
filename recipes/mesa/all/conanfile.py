from build import *


class MesaRecipe(Recipe):
    description = "An open-source implementation of the OpenGL specification"
    license = "custom"
    options = {"x11": [True, False]}
    default_options = ("x11=True",)
    build_requires = (
        "meson/[^0.55.3]",
        "gettext/[^0.21]",
        "bison/[^3.3]",
        "flex/[^2.6.4]",
        "python-mako/[^1.1.0]",
        "zlib/[^1.2.11]",
        "expat/[^2.2.7]",
        "libdrm/[^2.4.99]",
    )
    requires = ("libglvnd/[^1.3.2]",)

    def build_requirements(self):
        self.build_requires(f"llvm/[^{self.settings.clang.version}]")
        if self.options.x11:
            self.build_requires("libx11/[^1.6.8]")
            self.build_requires("libxrandr/[^1.5.2]")
            self.build_requires("libxdamage/[^1.1.5]")
            self.build_requires("libxshmfence/[^1.3]")
            self.build_requires("libxxf86vm/[^1.1.4]")

    def source(self):
        self.get(f"https://mesa.freedesktop.org/archive/mesa-{self.version}.tar.xz")

    def build(self):
        args = [
            "-Dglvnd=true",
            "-Dglx=dri",
            "-Degl=true",
            "-Dgles2=enabled",
            "-Dgles3=enabled",
        ]
        if self.options.x11:
            args.append("-Dplatforms=x11")
        if self.settings.arch_build == "x86_64":
            args.append("-Ddri-drivers=i915,i965")
            args.append("-Dgallium-drivers=iris")
            args.append("-Dvulkan-drivers=intel")
        if self.settings.arch_build == "armv8":
            args.append("-Dgallium-drivers=nouveau,tegra")
        self.meson(args)

    def package_info(self):
        self.env_info.LIBGL_DRIVERS_PATH.append(os.path.join(self.package_folder, "lib", "dri"))
