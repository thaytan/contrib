import os

from conans import ConanFile, Meson, tools


class LibdrmConan(ConanFile):
    name = "libdrm"
    version = tools.get_env("GIT_TAG", "2.4.99")
    license = "MIT"
    description = "Direct Rendering Manager headers and kernel modules"
    settings = "os", "arch", "compiler", "build_type"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("meson/[>=0.51.2]@%s/stable" % self.user)

    def requirements(self):
        self.requires("libpciaccess/[>=0.14]@%s/stable" % self.user)

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
