from build import *


class Lldb(Recipe):
    description = "Next generation, high-performance debugger"
    license = "custom:Apache 2.0 with LLVM Exception"
    build_requires = (
        "cc/[^1.0.0]",
        "cmake/[^3.18.4]",
    )
    requires = (
        "llvm/[^11.0.1]",
        "python/[^3.8.5]",
        "python-six/[^1.15.0]",
    )

    def source(self):
        self.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/llvm-{self.version}.src.tar.xz")
        self.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/clang-{self.version}.src.tar.xz", os.path.join(self.src, "projects", "clang"))
        self.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/lldb-{self.version}.src.tar.xz", os.path.join(self.src, "projects", "lldb"))

    def build(self):
        defs = {}
        self.cmake(
            defs,
            targets=["install-lldb"],
        )
