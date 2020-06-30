import os

from conans import ConanFile, Meson, tools


class GStreamerConan(ConanFile):
    description = "A framework for streaming media"
    license = "LGPL"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    options = {
        "introspection": [True, False],
        "check": [True, False],
        "tools": [True, False],
    }
    default_options = (
        "introspection=True",
        "check=True",
        "tools=True",
    )

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("meson/[>=0.51.2]@%s/stable" % self.user)
        self.build_requires("bison/[>=3.3]@%s/stable" % self.user)
        self.build_requires("flex/[>=2.6.4]@%s/stable" % self.user)
        if self.options.introspection:
            self.build_requires("gobject-introspection/[>=1.59.3]@%s/stable" % self.user,)

    def requirements(self):
        self.requires("glib/[>=2.62.0]@%s/stable" % self.user)

    def source(self):
        git = tools.Git(folder="%s-%s" % (self.name, self.version))
        git.clone(
            url="https://gitlab.freedesktop.org/gstreamer/gstreamer.git", branch=self.version, shallow=True,
        )

    def build(self):
        args = ["--auto-features=disabled"]
        args.append("-Dintrospection=" + ("enabled" if self.options.introspection else "disabled"))
        args.append("-Dcheck=" + ("enabled" if self.options.check else "disabled"))
        args.append("-Dtools=" + ("enabled" if self.options.tools else "disabled"))
        meson = Meson(self)
        meson.configure(
            source_folder="%s-%s" % (self.name, self.version), args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"),
        )
        meson.install()

    def package_info(self):
        self.env_info.GST_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
        self.env_info.GST_PLUGIN_SCANNER = os.path.join(self.package_folder, "bin", "gstreamer-1.0", "gst-plugin-scanner")
        self.env_info.GI_TYPELIB_PATH.append(os.path.join(self.package_folder, "lib", "girepository-1.0"))
