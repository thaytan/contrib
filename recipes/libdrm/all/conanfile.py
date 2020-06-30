import os

from conans import ConanFile, Meson, tools


class LibdrmConan(ConanFile):
    description = "Direct Rendering Manager headers and kernel modules"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0")
        self.build_requires("meson/[^0.51.2]")

    def requirements(self):
        self.requires("libpciaccess/[^0.14]")

    def source(self):
        tools.get("http://dri.freedesktop.org/libdrm/libdrm-%s.tar.gz" % self.version)

    def build(self):
        args = [
            "--auto-features=disabled",
            "-Dradeon=false",
            "-Damdgpu=false",
            "-Dnouveau=true",
        ]
        meson = Meson(self)
        meson.configure(source_folder="%s-%s" % (self.name, self.version), args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()
