import os
from conans import ConanFile, Meson, tools

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

class LibNiceConan(ConanFile):
    name = "libnice"
    version = tools.get_env("GIT_TAG", "0.1.15")
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "An implementation of the IETF's Interactive Connectivity Establishment (ICE) standard"
    license = "LGPL"
    settings = "os", "arch", "compiler", "build_type"
    options = {"gstreamer": [True, False]}
    default_options = "gstreamer=True"
    generators = "env"

    def build_requirements(self):
        self.build_requires("meson/[>=0.51.2]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.requires("glib/[>=2.62.0]@%s/stable" % self.user)
        self.requires("openssl/[>=1.1.1b]@%s/stable" % self.user)
        if self.options.gstreamer:
            gst_version = "1.16.0"
            self.requires("gstreamer-plugins-base/[>=%s <%s]@%s/stable" % (gst_version,get_upper_version_bound(gst_version, "0.1.0"), self.user))

    def source(self):
        tools.get("https://github.com/libnice/libnice/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--auto-features=disabled"]
        args.append(
            "-Dgstreamer=" + ("enabled" if self.options.gstreamer else "disabled")
        )
        meson = Meson(self)
        meson.configure(source_folder="%s-%s" % (self.name, self.version), args=args)
        meson.install()

    def package_info(self):
        self.env_info.GST_PLUGIN_PATH.append(
            os.path.join(self.package_folder, "lib", "gstreamer-1.0")
        )
