from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os
import platform

class LibffiConan(ConanFile):
    name = 'libffi'
    version = '3.2.1'
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'https://github.com/prozum/conan-libffi'
    license = 'https://github.com/libffi/libffi/blob/master/LICENSE'
    description = 'A portable, high level programming interface to various calling conventions'
    source_subfolder = 'source'
    build_subfolder = source_subfolder
    generators = "pkg_config"

    def source(self):
        tools.get('https://sourceware.org/pub/libffi/libffi-%s.tar.gz' % self.version,
                  sha256='d06ebb8e1d9a22d19e38d63fdb83954253f39bedc5d46232a05645685722ca37')
        os.rename("libffi-" + self.version, self.source_subfolder)

    def build(self):
        tools.mkdir(self.build_subfolder)
        with tools.chdir(self.build_subfolder):
            self.run("autoconf")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=['--quiet',
                                      '--disable-debug',
                                      '--disable-dependency-tracking',
                                      '--disable-static',
                                      '--enable-shared',
                                      '--prefix=%s' % os.getcwd()])
            autotools.make(args=['install'])

    def package(self):
        libext = 'so'

        self.copy('*.h', src='%s/include' % self.build_subfolder, dst='include')
        self.copy('*.h', src='%s/x86_64-unknown-linux-gnu/include/' % self.build_subfolder, dst='include')
        self.copy('libffi.%s' % libext, src='%s/lib' % self.build_subfolder, dst='lib')
        self.copy(pattern='*.pc', dst='', keep_path=False)

        self.copy('%s.txt' % self.name, src=self.source_subfolder, dst='license')

    def package_info(self):
        self.cpp_info.libs = ['ffi']
