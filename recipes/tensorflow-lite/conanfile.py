import os
from os.path import join
import re
from build import *

from conans import AutoToolsBuildEnvironment, ConanFile, tools

class TensorflowLite(Recipe):
    description = "https://www.tensorflow.org"
    license = "LGPL"
   
    build_requires = (
        "autotools/[^1.0.0]",
        "cc/[^1.0.0]", 
        "cmake/[^3.18.4]"
    )
    scm = dict(type="git",
               url="https://github.com/tensorflow/tensorflow.git",
               revision=f"4c0b84bf2a714bcdd18da1f1f94d533d72399d52")

    def build(self):
        env_build = AutoToolsBuildEnvironment(self)
        with tools.environment_append(env_build.vars):
            self.run("cmake tensorflow/lite -DTFLITE_ENABLE_GPU=ON")
            self.run("cmake --build . -j")
        
    def package(self):
        self.copy(pattern="*/libtensorflow-lite.*", dst="lib", src=f"tensorflow/lite", keep_path=False)
        self.copy(pattern="*.h", dst="include/tensorflow/lite", src=f"tensorflow/lite", keep_path=True)

    def package_info(self):
        self.cpp_info.libs = ["tensorflow-lite", "stdc++"]
        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["c", "m", "dl", "rt", "pthread"])