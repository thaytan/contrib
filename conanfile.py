from conans import CMake, ConanFile, tools


class LibvncserverConan(ConanFile):
    name = "libvncserver"
    version = tools.get_env("GIT_TAG", "0.9.12")
    license = "Apache"
    description = "Cross-platform C libraries that allow you to easily implement VNC server or client functionality"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    settings = "os", "compiler", "arch"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("cmake/[>=3.15.3]@%s/stable" % self.user)

    def requirements(self):
        self.requires("libpng/[>=1.6.37]@%s/stable" % self.user)
        self.requires("openssl/[>=1.1.1b]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/LibVNC/libvncserver/archive/LibVNCServer-%s.tar.gz" % self.version)

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.configure(source_folder="libvncserver-LibVNCServer-%s" % self.version)
        cmake.build()
        cmake.install()
