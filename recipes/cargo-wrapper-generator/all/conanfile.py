from conans import ConanFile, tools
from conans.model import Generator


class ConanCargoWrapper(Generator):
    @property
    def filename(self):
        return "conan_cargo_build.rs"

    @property
    def content(self):
        template = '''
fn main() {
}

pub const LIB_PATHS: &'static [ &'static str ] = &[%(lib_paths)s];
pub const LIBS: &'static [ &'static str ] = &[%(libs)s];
pub const INCLUDE_PATHS: &'static [ &'static str ] = &[%(include_paths)s];
'''

        def append_to_template(line):
            return template.replace("}", "    %s\n}" % line)

        def comma_separate(l):
            return ", ".join(['r#"%s"#' % x for x in l])

        for lib_path in self.deps_build_info.lib_paths:
            new = 'println!(r#"cargo:rustc-link-search=native=%s"#);' % lib_path
            template = append_to_template(new)

        for lib in self.deps_build_info.libs:
            new = 'println!(r#"cargo:rustc-link-lib=%s"#);' % lib
            template = append_to_template(new)

        for lib in self.deps_build_info.include_paths:
            new = 'println!(r#"cargo:include=%s"#);' % lib
            template = append_to_template(new)

        template = template % {
            "lib_paths": comma_separate(self.deps_build_info.lib_paths),
            "libs": comma_separate(self.deps_build_info.libs),
            "include_paths": comma_separate(self.deps_build_info.include_paths)
        }
        return template


class CargoGeneratorPackage(ConanFile):
    name = "ConanCargoWrapper"
    version = tools.get_env("GIT_TAG", "0.1")
    description = "Cargo integration generator"
    license = "MIT"
    settings = None

    def build(self):
        pass

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = []
