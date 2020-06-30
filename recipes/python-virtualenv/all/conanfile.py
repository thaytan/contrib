import os

from conans import ConanFile, tools


class PythonVirtualenvConan(ConanFile):
    license = "MIT"
    description = "Virtual Python Environment builder"
    settings = "os", "compiler", "build_type", "arch"

    def source(self):
        tools.get("https://github.com/pypa/virtualenv/archive/%s.tar.gz" % self.version)

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)

    def requirements(self):
        self.requires("python/[>=3.7.4]@%s/stable" % self.user)
        self.requires("python-setuptools/[>=41.2.0]@%s/stable" % self.user)
        self.requires("python-appdirs/[>=1.4.4]@%s/stable" % self.user)
        self.requires("python-distlib/[>=0.3.0]@%s/stable" % self.user)
        self.requires("python-filelock/[>=3.0.12]@%s/stable" % self.user)
        self.requires("python-six/[>=1.15.0]@%s/stable" % self.user)
        self.requires("python-importlib-metadata/[>=1.6.0]@%s/stable" % self.user)

    def build(self):
        env = {
            "SETUPTOOLS_SCM_PRETEND_VERSION": self.version,
        }
        with tools.chdir("virtualenv-%s" % self.version), tools.environment_append(env):
            self.run(
                'python setup.py install --optimize=1 --prefix= --root="%s"'
                % self.package_folder
            )

