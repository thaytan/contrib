from build import *


class NpmRecipe(Recipe):
    description = "Evented I/O for V8 javascript"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build", "python"
    build_requires = (
        "autotools/1.0.0",
        "libpng/[^1.6.37]",
        "mozjpeg/[^3.3.1]",
        "pngquant/[^2.12.6]",
    )
    requires = ("nodejs/[^13.0.1]",)

    def build_requirements(self):
        self.build_requires(f"python/[~{self.settings.python}]")

    def source(self):
        self.get(f"https://github.com/npm/cli/archive/v{self.version}.tar.gz")

    def build(self):
        pngquant_src = os.path.join(self.deps_cpp_info["pngquant"].rootpath, "bin", "pngquant")
        pngquant_dir = os.path.join(f"cli-{self.version}", "docs", "node_modules", "pngquant-bin", "vendor")
        os.makedirs(pngquant_dir)
        pngquant_dst = os.path.join(pngquant_dir, "pngquant")
        shutil.copy2(pngquant_src, pngquant_dst)
        with tools.chdir(f"cli-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            self.run("mkdir -p man/man1")
            autotools.install([f'NPMOPTS=--prefix="{self.package_folder}"'])
