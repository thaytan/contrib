import os

from conans import ConanFile, tools


class MesonConan(ConanFile):
    name = "meson"
    version = tools.get_env("GIT_TAG", "0.51.2")
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "Apache"
    description = "High productivity build system"
    settings = "os", "compiler", "build_type", "arch"
    generators = "env"

    def source(self):
        tools.get(
            "https://github.com/mesonbuild/meson/releases/download/{0}/meson-{0}.tar.gz".format(
                self.version
            )
        )

    def build_requirements(self):
        self.build_requires("python-setuptools/[>=41.2.0]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.requires("python/[>=3.7.4]@%s/stable" % self.user)
        self.requires("ninja/[>=1.9.0]@%s/stable" % self.user)
        self.requires("pkgconf/[>=1.6.3]@%s/stable" % self.user)
        self.requires("gcc/[>=7.4.0]@%s/stable" % self.user)

    def build(self):
        py_path = os.path.join(self.package_folder, "lib", "python", "site-packages")
        env = {"PYTHONPATH": py_path}
        os.makedirs(py_path)
        with tools.chdir("%s-%s" % (self.name, self.version)), tools.environment_append(
            env
        ):
            self.run(
                'python3 setup.py install --optimize=1 --prefix="%s"'
                % self.package_folder
            )

    def package_info(self):
        self.env_info.PYTHONPATH.append(
            os.path.join(self.package_folder, "lib", "python", "site-packages")
        )
