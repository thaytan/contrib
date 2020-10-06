import os

from conans import *
from six import StringIO
import shutil


TEMPLATE = """
[llvm]
[build]
target = ["x86_64-unknown-linux-gnu"]
tools = ["cargo", "rls", "clippy", "miri", "rustfmt", "analysis", "src"]
extended = true
sanitizers = false
profiler = true
vendor = true
[install]
prefix = "{0}"
[rust]
# LLVM crashes when passing an object through ThinLTO twice.  This is triggered when using rust
# code in cross-language LTO if libstd was built using ThinLTO.
# http://blog.llvm.org/2019/09/closing-gap-cross-language-lto-between.html
# https://github.com/rust-lang/rust/issues/54872
codegen-units-std = 1
debuginfo-level-std = 2
channel = "stable"
rpath = false
[target.x86_64-unknown-linux-gnu]
"""


class RustConan(ConanFile):
    llvm_version = "10.0.1"
    description = "Systems programming language focused on safety, speed and concurrency"
    license = "MIT", "Apache"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "llvm/[^10.0.1]",
        "python/[^3.8.5]",
    )

    def source(self):
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.llvm_version}/compiler-rt-{self.llvm_version}.src.tar.xz")
        tools.get(f"https://static.rust-lang.org/dist/rustc-{self.version}-src.tar.gz")

    def build(self):
        env = {
            "RUST_COMPILER_RT_ROOT": os.path.join(self.source_folder, f"compiler-rt-{self.llvm_version}"),
        }
        with tools.chdir(f"rustc-{self.version}-src"), tools.environment_append(env):
            with open("config.toml", "w") as config:
                content = TEMPLATE.format(self.package_folder)
                config.write(content)

            self.run("python x.py dist")
