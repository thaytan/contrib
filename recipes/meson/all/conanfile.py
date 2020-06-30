import os

from conans import ConanFile, tools


class MesonConan(ConanFile):
    description = "High productivity build system"
    license = "Apache"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def source(self):
        tools.get("https://github.com/mesonbuild/meson/releases/download/{0}/meson-{0}.tar.gz".format(self.version))

    def build_requirements(self):
        self.build_requires("generators/1.0.0")

    def requirements(self):
        self.requires("python/[^3.7.4]")
        self.requires("python-setuptools/[^41.2.0]")
        self.requires("ninja/[^1.9.0]")
        self.requires("pkgconf/[^1.6.3]")
        self.requires("cc/[^1.0.0]")

    def build(self):
        py_path = os.path.join(self.package_folder, "lib", "python3.7", "site-packages")
        env = {"PYTHONPATH": os.environ["PYTHONPATH"] + os.pathsep + py_path}
        os.makedirs(py_path)
        with tools.chdir("%s-%s" % (self.name, self.version)), tools.environment_append(env):
            self.run('python setup.py install --optimize=1 --prefix= --root="%s"' % self.package_folder)

    def package_info(self):
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "lib", "python3.7", "site-packages"))
