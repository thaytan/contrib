import os

from conans import ConanFile, Meson, tools


class LibxcbConan(ConanFile):
    description = "Keymap handling library for toolkits and window systems"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("meson/[>=0.51.2]@%s/stable" % self.user)
        self.build_requires("bison/[>=3.3]@%s/stable" % self.user)
        self.build_requires("flex/[>=2.6.4]@%s/stable" % self.user)

    def requirements(self):
        self.requires("libxcb/[>=1.13.1]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/xkbcommon/libxkbcommon/archive/xkbcommon-%s.tar.gz" % self.version)

    def build(self):
        args = [
            "--auto-features=disabled",
            "-Denable-wayland=false",
            "-Denable-docs=false",
        ]
        meson = Meson(self)
        meson.configure(source_folder="libxkbcommon-xkbcommon-" + self.version, args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.install()
