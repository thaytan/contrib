import os

from conans import ConanFile, tools


class PythonMakoConan(ConanFile):
    name = "python-mako"
    version = tools.get_env("GIT_TAG", "1.1.0")
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "Apache"
    description = "A super-fast templating language that borrows the best ideas from the existing templating languages"
    settings = "os", "compiler", "build_type", "arch"

    def source(self):
        tools.get("https://github.com/sqlalchemy/mako/archive/rel_%s.tar.gz" % self.version.replace(".", "_"))

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("python-setuptools/[>=41.2.0]@%s/stable" % self.user)

    def requirements(self):
        self.requires("python/[>=3.7.4]@%s/stable" % self.user)

    def build(self):
        with tools.chdir("mako-rel_" + self.version.replace(".", "_")):
            self.run('python setup.py install --optimize=1 --prefix= --root="%s"' % self.package_folder)

    def package_info(self):
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "lib", "python3.7", "site-packages"))
