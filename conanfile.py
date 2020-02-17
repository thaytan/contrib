import os

from conans import ConanFile, tools


class PythonPipConan(ConanFile):
    name = "python-pip"
    version = tools.get_env("GIT_TAG", "19.2.3")
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "MIT"
    description = "High productivity build system"
    settings = "os", "compiler", "build_type", "arch"

    def source(self):
        tools.get("https://github.com/pypa/pip/archive/%s.tar.gz" % self.version)

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("python-setuptools/[>=41.2.0]@%s/stable" % self.user)

    def requirements(self):
        self.requires("python/[>=3.7.4]@%s/stable" % self.user)

    def build(self):
        with tools.chdir("pip-" + self.version):
            self.run('python setup.py install --optimize=1 --prefix= --root="%s"' % self.package_folder)

    def package_info(self):
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "lib", "python3.7", "site-packages"))
