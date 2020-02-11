import os

from conans import ConanFile, tools


class RustConan(ConanFile):
    name = "rust"
    version = tools.get_env("GIT_TAG", "nightly")
    settings = "os", "compiler", "arch"
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
            self.run("./bin/rustup component add rust-src")

    def package(self):
        arch = {"x86_64": "x86_64", "armv8": "aarch64"}[str(self.settings.arch)]
        src = os.path.join("toolchains", "%s-%s-unknown-linux-gnu" % (self.version, arch))
        self.copy("*", src=os.path.join(src, "bin"), dst="bin")
        self.copy("*.so*", src=os.path.join(src, "lib"), dst="lib")
        self.copy("*", src=os.path.join(src, "etc", "bash_completion.d"), dst=os.path.join("share", "bash-completion", "completions"))
        self.copy("*", src=os.path.join(src, "lib", "rustlib"), dst=os.path.join("lib", "rustlib"))

    def package_info(self):
        self.env_info.RUST_SRC_PATH = os.path.join(self.package_folder, "lib", "rustlib", "src", "rust", "src")
