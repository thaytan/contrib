from conans import ConanFile, tools, Meson
import os

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "2.3.0"
    except:
        return None

class IntelVaapiDriverConan(ConanFile):
    name = "intel-vaapi-driver"
    version = get_version()
    license = "MIT"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "VA-API user mode driver for Intel GEN Graphics family"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def build_requirements(self):
        self.build_requires("cmake/[>=3.15.3]@%s/stable" % (self.user))

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.requires("libdrm/[>=2.4.96]@%s/stable" % self.user)
        self.requires("libva/[>=2.3.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/intel/intel-vaapi-driver/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["-Ddriverdir=" + os.path.join(self.package_folder, "lib", "dri")]
        meson = Meson(self)
        meson.configure(source_folder="intel-vaapi-driver-" + self.version, args=args)
        meson.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.LIBVA_DRIVERS_PATH.append(os.path.join(self.package_folder, "lib", "dri"))
