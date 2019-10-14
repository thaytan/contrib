from conans import ConanFile, Meson, tools
import os

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "1.16.0"
    except:
        return None

class GStreamerDevtoolsConan(ConanFile):
    name = "gstreamer-devtools"
    version = get_version()
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "Development and debugging tools for GStreamer"
    license = "LGPL"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"
    scm = {
        "type": "git",
        "url": "https://gitlab.com/aivero/public/gstreamer/gst-devtools-mirror",
        "revision": "155-add-psnr",
        "recursive": True,
        "subfolder": ("gst-devtools-" + version)
    }

    def build_requirements(self):
        self.build_requires("meson/[>=0.51.2]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.requires("gstreamer-plugins-base/[>=%s]@%s/stable" % (self.version, self.user))
        self.requires("json-glib/[>=1.4.4]@%s/stable" % self.user)

    def build(self):
        args = ["--auto-features=disabled"]
        meson = Meson(self)
        meson.configure(source_folder="gst-devtools-" + self.version, args=args)
        meson.install()

    def package(self):
        self.copy("*.so*", dst=os.path.join(self.package_folder, "lib", "gstreamer-1.0"), keep_path=False)

    def deploy(self):
        install_path = os.getcwd()
        # Binaries
        self.copy("*gst-*", dst="bin", keep_path=False)

        # Gstreamer binaries
        self.copy_deps("*gst-inspect-1.0", dst="bin", keep_path=False)
        self.copy_deps("*gst-launch-1.0", dst="bin", keep_path=False)
        self.copy_deps("*gst-plugin-scanner", dst="bin", keep_path=False)

        # Libraries
        self.copy_deps("*.so*")
        self.copy("*.so*", dst=os.path.join("lib", "gstreamer-1.0"), keep_path=False)

        # Pkg - config files
        deps = ["depth-*", "gstreamer*", "orc-0.4"]
        for dep in deps:
            self.copy_deps("*%s.pc" % dep, dst="lib/pkgconfig", keep_path=False)

        for pc_file in os.listdir("lib/pkgconfig"):
            tools.replace_prefix_in_pc_file(os.path.join("lib", "pkgconfig", pc_file), install_path)

        # Environment script
        with open(os.path.join(install_path, "dddq_environment.sh"), "w+") as env_file:
            env_file.write("export PREFIX=" + install_path)
            env_file.write("\nexport PATH=" + os.path.join("$PREFIX", "bin") + ":$PATH")
            env_file.write("\nexport LD_LIBRARY_PATH=" + os.path.join("$PREFIX", "lib") + ":"  + os.path.join("$PREFIX", "lib/gstreamer-1.0") + ":$LD_LIBRARY_PATH")
            env_file.write("\nexport PKG_CONFIG_PATH=" + os.path.join("$PREFIX", "lib", "pkgconfig"))
            env_file.write("\nexport GST_PLUGIN_PATH=" + os.path.join("$PREFIX", "lib", "gstreamer-1.0") + ":" + os.path.join("$PREFIX", "lib", "depth_receiver"))
            env_file.write("\nexport GST_PLUGIN_SCANNER=" + os.path.join("$PREFIX", "bin", "gst-plugin-scanner"))

