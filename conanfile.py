from conans import ConanFile, Meson, tools
import os

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "0.2.12"
    except:
        return None

class SccacheConan(ConanFile):
    name = "sccache"
    version = get_version()
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "Development and debugging tools for GStreamer"
    license = "Apache2"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def source(self):
        tools.get("https://github.com/mozilla/sccache/archive/{}.tar.gz".format(self.version))

    def build_requirements(self):
        self.build_requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.build_requires("rust/[>=1.3.8]@%s/stable" % self.user)
        self.build_requires("openssl/[>=1.1.1b]@%s/stable" % self.user)

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            self.run("RUSTC_WRAPPER=sccache cargo build --release")

    def package(self):
        self.copy(pattern="*/sccache", dst=os.path.join(self.package_folder, "bin"), keep_path=False)
