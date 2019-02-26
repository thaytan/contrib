from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os
import platform

class LibffiConan(ConanFile):
    name = "libffi"
    version = "3.3-rc0"
    default_user = "bincrafters"
    settings = "os", "compiler", "build_type", "arch"
    url = "https://github.com/prozum/conan-libffi"
    license = "https://github.com/libffi/libffi/blob/master/LICENSE"
    description = "A portable, high level programming interface to various calling conventions"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"
    folder_name = name + "-" + version
    no_copy_source = True

    def source(self):
        tools.get("https://github.com/libffi/libffi/archive/v%s.tar.gz" % self.version)

    def build(self):
        args = [
            "--quiet",
            "--disable-debug",
            "--disable-dependency-tracking",
            "--disable-docs"
        ]
        if self.options.shared:
            args.extend(["--disable-static", "--enable-shared"])
        else:
            args.extend(["--disable-shared", "--enable-static"])
        with tools.chdir(os.path.join(self.source_folder, self.folder_name)):
            self.run("./autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()

    def package(self):
        if self.channel == "testing":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.PKG_CONFIG_LIBFFI_PREFIX = self.package_folder
        self.env_info.PKG_CONFIG_PATH.append(os.path.join(self.package_folder, "lib", "pkgconfig"))
        self.env_info.SOURCE_PATH.append(os.path.join(self.package_folder, "src"))
        self.cpp_info.srcdirs.append("src")
