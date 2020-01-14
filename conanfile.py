from conans import ConanFile, Meson, tools
import os

def get_upper_version_bound(version, version_diff):
    try:
        v = tools.Version(version)
    except:
        print("Input version is not a valid SemVer")
    try:
        v_diff = tools.Version(version_diff)
        version_out = "%d.%d.%d" % ((int(v.major) + int(v_diff.major)),(int(v.minor) + int(v_diff.minor)), (int(v.patch) + int(v_diff.patch)))
        if v.prerelease:
            version_out = version_out + "-" + v.prerelease
        elif v_diff.prerelease:
            version_out = version_out + "-" + v_diff.prerelease
        return version_out
    except Exception as e:
        print(e)
        print("Version diff is not a valid SemVer")

class GStreamerLibavConan(ConanFile):


    name = "gstreamer-libav"
    version = tools.get_env("GIT_TAG", "1.16.0")
    upper_version_bound = get_upper_version_bound(version, "0.1.0")

    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "GStreamer plugin for the libav* library (former FFmpeg)"
    license = "GPL"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def build_requirements(self):
        self.build_requires("meson/[>=0.51.2]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.requires("glib/[>=2.58.1]@%s/stable" % self.user)
        self.requires("gstreamer-plugins-base/[>=%s <%s]@%s/stable" % (self.version, self.upper_version_bound, self.user))
        self.requires("ffmpeg/[>=4.1]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/GStreamer/gst-libav/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--auto-features=disabled"]
        meson = Meson(self)
        meson.configure(source_folder="gst-libav-" + self.version, args=args)
        meson.install()

    def package_info(self):
        self.env_info.GST_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
