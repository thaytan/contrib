from conans import ConanFile, Meson, tools
import os

class GStreamerDevtoolsConan(ConanFile):
    name = "gstreamer-devtools"
    version = tools.get_env("GIT_TAG", "1.16.0")
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "Development and debugging tools for GStreamer"
    license = "LGPL"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"
    scm = {
        "type": "git",
        "url": "https://gitlab.com/aivero/public/gstreamer/gst-devtools-mirror",
        "revision": "rebased-155-add-psnr",
        "recursive": True,
        "subfolder": ("gst-devtools-" + version)
    }
    options = {"intel": [True, False], "ffmpeg": [True, False]}
    default_options = "intel=True", "ffmpeg=False"

    def build_requirements(self):
        self.build_requires("meson/[>=0.51.2]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.requires("gstreamer-plugins-base/[>=%s]@%s/stable" % (self.version, self.user))
        self.requires("gstreamer/[>=%s]@%s/stable" % (self.version, self.user))
        self.requires("json-glib/[>=1.4.4]@%s/stable" % self.user)

        # Temporarely in here to give easy access to encoders etc. 
        self.requires("depth-receiver/[>=0.7.1]@%s/stable" % self.user)
        if self.settings.arch == "x86_64":
            if self.options.intel:
                self.requires("intel-vaapi-driver/[>=2.3.0]@%s/stable" % self.user)
                self.requires("gstreamer-vaapi/%s@%s/stable" % (self.version, self.user))
            if self.options.ffmpeg:
                self.requires("gstreamer-libav/%s@%s/stable" % (self.version, self.user))
        elif self.settings.arch == "armv8":
            self.requires("gstreamer-omx-tx2/%s@%s/stable" % (self.version, self.user))
            self.requires("jetson-drivers/[>=32.2.1]@%s/stable" % self.user)

    def build(self):
        meson = Meson(self)
        meson.configure(source_folder="gst-devtools-" + self.version)
        meson.install()

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
        self.copy("*.so*", keep_path=True)

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
            env_file.write("\nexport GST_VALIDATE_PLUGIN_PATH=" + os.path.join("$PREFIX", "lib", "gstreamer-1.0", "validate"))
