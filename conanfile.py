import os

from conans import ConanFile, tools


def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "1.38.0"
    except:
        return None


class RustConan(ConanFile):
    name = "rust"
    version = get_version()
    settings = "os", "compiler", "build_type", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "MIT", "Apache"
    description = (
        "Systems programming language focused on safety, speed and concurrency"
    )
    generators = "env"

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.requires("pkgconf/[>=1.6.3]@%s/stable" % self.user)

    def source(self):
        tools.download("https://sh.rustup.rs", "rustup.sh")

    def build(self):
        env = {
            "RUSTUP_HOME": os.path.join(self.package_folder, "rustup"),
            "CARGO_HOME": self.package_folder,
        }
        with tools.environment_append(env):
            self.run("sh rustup.sh -y --default-toolchain " + self.version)

    def package_info(self):
        self.env_info.RUSTUP_HOME = os.path.join(self.package_folder, "rustup")
        self.env_info.CARGO_HOME = self.package_folder
