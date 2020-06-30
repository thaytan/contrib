from conans import ConanFile, tools
import os


class GlmConan(ConanFile):
    description = "OpenGL Mathematics (GLM) is a header only C++ mathematics library for graphics software based on the OpenGL Shading Language (GLSL) specifications."
    license = "MIT License"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    exports_sources = ["glm.pc"]

    def source(self):
        tools.get("https://github.com/g-truc/glm/releases/download/%s/glm-%s.zip" % (self.version, self.version))

    def package(self):
        self.copy(pattern="*", src="glm/glm", dst=os.path.join(self.package_folder, "include", "glm"), keep_path=True)
        self.copy(pattern="glm.pc", dst=os.path.join(self.package_folder, "lib", "pkgconfig"), keep_path=False)
