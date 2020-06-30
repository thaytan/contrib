from conans import ConanFile, tools


class PythonDistlibConan(ConanFile):
    description = "Low-level components of distutils2/packaging"
    license = "PSF"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0")

    def requirements(self):
        self.requires("python/[^3.7.4]")

    def source(self):
        tools.get("https://files.pythonhosted.org/packages/source/d/distlib/distlib-{0}.zip".format(self.version))

    def build(self):
        with tools.chdir("distlib-{}".format(self.version)):
            self.run('python setup.py install --optimize=1 --prefix= --root="{}"'.format(self.package_folder))
