from conans import ConanFile, tools
import os

class GlmConan(ConanFile):
    name = "glm"
    settings = "os", "compiler", "build_type", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "MIT License"
    description = "OpenGL Mathematics (GLM) is a header only C++ mathematics library for graphics software based on the OpenGL Shading Language (GLSL) specifications."
    generators = "env"
    exports_sources = ["glm.pc"]

    def build_requirements(self):
        self.build_requires("env-generator/1.0.0@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/g-truc/glm/releases/download/%s/glm-%s.zip" % (self.version, self.version))

    def package(self):
        self.copy(pattern="*",src="glm/glm", dst=os.path.join(self.package_folder, "include", "glm"), keep_path=True)
        self.copy(pattern="glm.pc", dst=os.path.join(self.package_folder, "lib", "pkgconfig"), keep_path=False)
