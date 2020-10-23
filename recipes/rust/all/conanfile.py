import os
from conans import *


class RustConan(ConanFile):
    description = "Systems programming language focused on safety, speed and concurrency"
    license = "MIT", "Apache"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build", "python"
    build_requires = (
        "llvm/[^11.0.0]",
        "cmake/[^3.18.0]",
        "ninja/[^1.10.0]",
        "curl/[^7.72.0]",
        "pkgconf/[^1.7.3]",
        "zlib/[^1.2.11]",
        "git/[2.28.0]",
    )
    requires = ("openssl1/[^1.1.1h]",)

    def build_requirements(self):
        self.build_requires(f"python/[~{self.settings.python}]")

    def source(self):
        tools.get(f"https://static.rust-lang.org/dist/rustc-{self.version}-src.tar.gz")

    def build(self):
        env = {
            "RUSTFLAGS": "-Clinker-plugin-lto -Copt-level=2",
            "CFLAGS": f"-I{os.path.join(self.deps_cpp_info['zlib'].rootpath, 'include')} {os.environ['CFLAGS']}",
        }
        arch = {"x86_64": "x86_64", "armv8": "aarch64"}[str(self.settings.arch_build)]
        triple = f"{arch}-unknown-linux-gnu"
        args = [
            f"--host={triple}",
            f"--target={triple}",
            f'--prefix="{self.package_folder}"',
            f"--llvm-root={self.deps_cpp_info['llvm'].rootpath}",
            "--enable-option-checking",
            "--enable-llvm-link-shared",
            "--enable-locked-deps",
            "--enable-extended",
            "--tools='cargo'",
            "--disable-docs",
            "--enable-vendor",
            "--release-channel=stable",
            "--set=llvm.thin-lto=true",
        ]
        with tools.chdir(f"rustc-{self.version}-src"), tools.environment_append(env):
            self.run(f"./configure {' '.join(args)}")
            self.run("python x.py install")

    def package_info(self):
        self.env_info.RUSTFLAGS = "-Clinker-plugin-lto -Copt-level=2"
