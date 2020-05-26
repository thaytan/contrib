import os

from conans import ConanFile, Meson, tools


class PythonCairoConan(ConanFile):
    name = "python-cairo"
    version = tools.get_env("GIT_TAG", "1.18.2")
    description = "Python bindings for the cairo graphics library"
    license = "LGPL2.1"
    settings = "os", "arch", "compiler", "build_type"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("gcc/[>=7.4.0]@%s/stable" % self.user)

    def requirements(self):
        self.requires("python/[>=3.7.4]@%s/stable" % self.user)
        self.requires("cairo/[>=1.16.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/pygobject/pycairo/releases/download/v{0}/pycairo-{0}.tar.gz".format(self.version))

    def build(self):
        with tools.chdir("pycairo-%s" % self.version):
            self.run('python setup.py install --optimize=1 --prefix= --root="%s"' % self.package_folder)

    def package_info(self):
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "lib", "python3.7", "site-packages"))
