from build import *


class CCRecipe(Recipe):
    description = "Virtual c/c++ compiler package"
    license = "MIT"

    def requirements(self):
        self.requires("libc/[^1.0.0]")
        self.requires(f"llvm/[^{self.settings.compiler.version}]")

    def package_info(self):
        static_flags = ""
        if self.settings.libc_build == "musl":
            static_flags = "-static"
        libc_inc = self.env["LIBC_INCLUDE_PATH"]
        clang_inc = os.path.join(self.deps_cpp_info["llvm"].rootpath, "lib", "clang", self.deps_cpp_info["llvm"].version, "include")
        libcxx_inc = os.path.join(self.deps_cpp_info["llvm"].rootpath, "include", "c++", "v1")
        # -Wno-unused-command-line-argument is needed for some sanity tests in cmake
        cflags = f" -nostdinc -idirafter {clang_inc} -idirafter {libc_inc} {static_flags} -fPIC -flto=thin -Wno-unused-command-line-argument "
        cxxflags = f" -nostdinc++ -idirafter {libcxx_inc} {cflags} "

        self.env_info.CFLAGS = cflags
        self.env_info.CXXFLAGS = cxxflags
