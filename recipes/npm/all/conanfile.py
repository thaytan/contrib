import os, shutil

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class NpmConan(ConanFile):
    description = "Evented I/O for V8 javascript"
    license = "MIT"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("autotools/1.0.0")
        self.build_requires("python/[^3.7.4]")
        self.build_requires("libpng/[^1.6.37]")
        self.build_requires("mozjpeg/[^3.3.1]")
        self.build_requires("pngquant/[^2.12.6]")

    def requirements(self):
        self.requires("generators/1.0.0")
        self.requires("nodejs/[^13.0.1]")

    def source(self):
        tools.get("https://github.com/npm/cli/archive/v%s.tar.gz" % self.version)

    def build(self):
        pngquant_src = os.path.join(self.deps_cpp_info["pngquant"].rootpath, "bin", "pngquant")
        pngquant_dir = os.path.join("cli-%s" % self.version, "docs", "node_modules", "pngquant-bin", "vendor")
        os.makedirs(pngquant_dir)
        pngquant_dst = os.path.join(pngquant_dir, "pngquant")
        shutil.copy2(pngquant_src, pngquant_dst)
        with tools.chdir("cli-%s" % self.version):
            autotools = AutoToolsBuildEnvironment(self)
            self.run("mkdir -p man/man1")
            autotools.install(['NPMOPTS=--prefix="%s"' % self.package_folder])
