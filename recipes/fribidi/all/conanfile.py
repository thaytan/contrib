import os

from conans import ConanFile, Meson, tools


class FribidiConan(ConanFile):
    description = "The Free Implementation of the Unicode Bidirectional Algorithm"
    license = "LGPL"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0")
        self.build_requires("meson/[^0.5.12]")

    def source(self):
        tools.get("https://github.com/fribidi/fribidi/archive/v%s.tar.gz" % self.version)

    def build(self):
        args = ["--auto-features=disabled", "-Ddocs=false"]
        meson = Meson(self)
        meson.configure(source_folder="%s-%s" % (self.name, self.version), args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()
