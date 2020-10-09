import os
from conans import *


class RustConan(ConanFile):
    llvm_version = "10.0.1"
    description = "Systems programming language focused on safety, speed and concurrency"
    license = "MIT", "Apache"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "bootstrap-llvm/[^10.0.1]",
        "bootstrap-cmake/[^3.18.0]",
        "bootstrap-ninja/[^1.10.0]",
        "python/[^3.8.5]",
        "curl/[^7.72.0]",
    )

    def source(self):
        tools.get(f"https://static.rust-lang.org/dist/rustc-{self.version}-src.tar.gz")

    def build(self):
        archs = {
            "x86_64": "x86_64",
            "armv8": "aarch64",
        }
        arch = archs[str(self.settings.arch_build)]
        triple = f"{arch}-aivero-linux-gnu"
        args = [
            f"--host={triple}",
            f"--target={triple}",
            f"--llvm-root={self.deps_cpp_info['bootstrap-llvm'].rootpath}",
            "--enable-vendor",
        ]
        with tools.chdir(f"rustc-{self.version}-src"):
            self.run(f"./configure {' '.join(args)}")
            # with open("config.toml") as r:
            #    text = r.read().replace("#thin-lto = false", "thin-lto = true")
            # with open("config.toml", "w") as w:
            #    w.write(text)
            self.run("python x.py dist")
