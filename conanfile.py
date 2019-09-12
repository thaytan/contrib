from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os
import stat

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "2.2.0"
    except:
        return None

class LibSrtpConan(ConanFile):
    name = "libsrtp"
    version = get_version()
    url = "http://gitlab.com/aivero/public/conan/conan-" + name
    license = "BSD"
    description = "Library for SRTP (Secure Realtime Transport Protocol)"
    settings = "os", "arch", "compiler", "build_type"

    def source(self):
        tools.get("https://github.com/cisco/libsrtp/archive/v%s.tar.gz" % self.version)

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make(args=["shared_library"])
            autotools.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.srcdirs.append("src")

