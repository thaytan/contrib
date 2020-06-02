import os

from conans import ConanFile, Meson, tools

class NumpyConan(ConanFile):
    name = "numpy"
    version = tools.get_env("GIT_TAG", "1.18.4")
    description = "conan package for Python Numpy module"
    license = "BSD"
    settings = "os", "arch", "compiler", "build_type"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("gcc/[>=7.4.0]@%s/stable" % self.user)
        self.build_requires("pkgconf/[>=1.6.3]@%s/stable" % self.user)
        self.build_requires("python-setuptools/[>=41.2.0]@%s/stable" % self.user)
        self.build_requires("cython/[>=0.29.19]@%s/stable" % self.user)

    def requirements(self):
        self.requires("python/[>=3.7.4]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/numpy/numpy/releases/download/v{0}/numpy-{0}.tar.gz".format(self.version))

    def build(self):
        with tools.chdir("numpy-{0}".format(self.version)):
            self.run('python setup.py install --optimize=1 --prefix= --root="%s"' % self.package_folder)

    def package_info(self):
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "lib", "python3.7", "site-packages"))



