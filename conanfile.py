from conans import ConanFile, Meson, tools
import os

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "1.16.0"
    except:
        return None

class GStreamerConan(ConanFile):
    name = "gstreamer"
    version = get_version()
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "A framework for streaming media"
    license = "https://gitlab.freedesktop.org/gstreamer/gstreamer/raw/master/COPYING"
    settings = "os", "arch", "compiler", "build_type"
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
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/stable" % self.user)
        self.requires("glib/2.58.1@%s/stable" % self.user)
        self.requires("bison/3.3@%s/stable" % self.user, private=True)
        self.requires("flex/2.6.4@%s/stable" % self.user, private=True)
        if self.options.introspection:
            self.requires("gobject-introspection/1.59.3@%s/stable" % self.user,)

    def source(self):
        tools.get("https://github.com/GStreamer/gstreamer/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--auto-features=disabled"]
        args.append("-Dintrospection=" + ("enabled" if self.options.introspection else "disabled"))
        args.append("-Dcheck=" + ("enabled" if self.options.check else "disabled"))
        args.append("-Dtools=" + ("enabled" if self.options.tools else "disabled"))
        meson = Meson(self)
        meson.configure(source_folder="%s-%s" % (self.name, self.version), args=args)
        meson.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.includedirs = ["include/gstreamer-1.0"]
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.srcdirs.append("src")
        self.env_info.GST_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
        self.env_info.GST_PLUGIN_SCANNER = os.path.join(self.package_folder, "bin", "gstreamer-1.0", "gst-plugin-scanner")
        self.env_info.GI_TYPELIB_PATH.append(os.path.join(self.package_folder, "lib", "girepository-1.0"))
