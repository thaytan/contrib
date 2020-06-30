import os

from conans import ConanFile, tools


class PythonMakoConan(ConanFile):
    description = "A super-fast templating language that borrows the best ideas from the existing templating languages"
    license = "Apache"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def source(self):
        tools.get("https://github.com/sqlalchemy/mako/archive/rel_%s.tar.gz" % self.version.replace(".", "_"))

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("python-setuptools/[^41.2.0]@%s/stable" % self.user)

    def requirements(self):
        self.requires("python/[^3.7.4]@%s/stable" % self.user)

    def build(self):
        with tools.chdir("mako-rel_" + self.version.replace(".", "_")):
            self.run('python setup.py install --optimize=1 --prefix= --root="%s"' % self.package_folder)

    def package_info(self):
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "lib", "python3.7", "site-packages"))
