from build import *


class RustRecipe(Recipe):
    description = "Systems programming language focused on safety, speed and concurrency"
    license = "MIT", "Apache"
    settings = Recipe.settings + ("python", "rust")
    build_requires = (
        "cmake/[^3.18.4]",
        "curl/[^7.72.0]",
        "pkgconf/[^1.7.3]",
        "git/[^2.29.1]",
    )
    requires = (
        "zlib/[^1.2.11]",
        "openssl1/[^1.1.1h]",
    )

    def build_requirements(self):
        self.build_requires(f"python/[~{self.settings.python}]")

    def requirements(self):
        self.requires(f"llvm/[^{self.settings.compiler.version}]")

    def source(self):
        self.get(f"https://static.rust-lang.org/dist/rustc-{self.version}-src.tar.gz")

    def build(self):
        os.environ["RUSTFLAGS"] = "-Clinker-plugin-lto -Copt-level=2"
        arch = {"x86_64": "x86_64", "armv8": "aarch64"}[str(self.settings.arch)]
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
            "--tools=cargo",
            "--disable-docs",
            "--enable-vendor",
            "--release-channel=stable",
            "--set=llvm.thin-lto=true",
        ]
        self.exe("./configure", args)
        self.exe("python x.py install")

    def package_info(self):
        self.env_info.RUSTFLAGS = "-Clinker-plugin-lto -Copt-level=2"
