from conans import ConanFile, tools
import os

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "0.51.2"
    except:
        return None

class MesonConan(ConanFile):
    name = "meson"
    version = get_version()
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "Apache"
    description = "High productivity build system"
    settings = "os", "compiler", "build_type", "arch"
    generators = "env"

    def source(self):
        tools.get("https://github.com/mesonbuild/meson/releases/download/{0}/meson-{0}.tar.gz".format(self.version))

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.requires("ninja/[>=1.9.0]@%s/stable" % self.user)
        self.requires("pkgconf/[>=1.6.3]@%s/stable" % self.user)

    def build(self):
        py_path = os.path.join(self.package_folder, "lib", "python3.6", "site-packages")
        env = {"PYTHONPATH": py_path}
        os.makedirs(py_path)
        with tools.chdir("%s-%s" % (self.name, self.version)), tools.environment_append(env):
            self.run("python3 setup.py install --optimize=1 --prefix=\"%s\"" % self.package_folder)

    def package_info(self):
        self.env_info.PYTHONPATH = os.path.join(self.package_folder, "lib", "python3.6", "site-packages")
