from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os
import platform

class LibffiConan(ConanFile):
    name = 'libffi'
    version = '3.3-rc0'
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'https://github.com/prozum/conan-libffi'
    license = 'https://github.com/libffi/libffi/blob/master/LICENSE'
    description = 'A portable, high level programming interface to various calling conventions'

    def source(self):
        tools.get("https://github.com/libffi/libffi/archive/v%s.tar.gz" % self.version)

    def build(self):
        with tools.chdir("libffi-" + self.version):
            self.run("autoreconf --install")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=['--quiet',
                                      '--disable-debug',
                                      '--disable-dependency-tracking',
                                      '--disable-docs',
                                      '--disable-static',
                                      '--enable-shared'])
            autotools.make()
            autotools.install()

    def package_info(self):
        self.env_info.PKG_CONFIG_PATH.append(os.path.join(self.package_folder, "lib", "pkgconfig"))
