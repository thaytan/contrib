import os

from conans import ConanFile, tools


class RustConan(ConanFile):
    name = "rust"
    version = tools.get_env("GIT_TAG", "1.38.0")
    settings = "os", "compiler", "build_type", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "MIT", "Apache"
    description = "Systems programming language focused on safety, speed and concurrency"
    generators = "env"

    def build_requirements(self):
        self.build_requires("env-generator/1.0.0@%s/stable" % self.user)
        self.build_requires("curl/[>=7.66.0]@%s/stable" % self.user)

    def requirements(self):
        self.requires("pkgconf/[>=1.6.3]@%s/stable" % self.user)
        self.requires("clang/[>=9.0.0]@%s/stable" % self.user)
        self.requires("gcc/[>=7.4.0]@%s/stable" % self.user)

    def source(self):
        tools.download("https://sh.rustup.rs", "rustup.sh")

    def build(self):
        env = {
            "HOME": self.build_folder,  # To avoid rustup writing to $HOME/.profile
            "RUSTUP_HOME": self.build_folder,
            "CARGO_HOME": self.build_folder,
        }
        with tools.environment_append(env):
            self.run("sh rustup.sh -y --default-toolchain " + self.version)

    def package(self):
        arch = {"x86_64": "x86_64", "armv8": "aarch64"}[str(self.settings.arch)]
        src = os.path.join("toolchains", "%s-%s-unknown-linux-gnu" % (self.version, arch))
        self.copy("*", src=os.path.join(src, "bin"), dst="bin", keep_path=False)
        self.copy("*.so*", src=os.path.join(src, "lib"), dst="lib", keep_path=False)
        self.copy(
            "*",
            src=os.path.join(src, "lib", "rustlib"),
            dst=os.path.join("lib", "rustlib"),
        )
