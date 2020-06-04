from conans import ConanFile, CMake, tools


class FMILibraryConan(ConanFile):
    name = "fmilibrary"
    version = "2.0.3"
    license = "https://svn.jmodelica.org/FMILibrary/tags/2.0.3/LICENSE.md"
    url = "https://github.com/kyllingstad/conan-FMILibrary"
    description = "An implementation of the FMI standard which enables FMU import in applications"
    scm = {
        "type": "git",
        "url": "https://github.com/modelon-community/fmi-library.git",
        "revision": version,
        "subfolder": "src"
    }
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = "cmake"
    exports_sources = [ "build-static-c99snprintf.patch" ]

    def source(self):
        tools.patch(base_path="src", patch_file="build-static-c99snprintf.patch")
        tools.replace_in_file("src/CMakeLists.txt", "project (FMILibrary)",
                              '''project (FMILibrary)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def build(self):
        cmake = CMake(self)
        cmake.configure(
            source_folder="src",
            defs={
                "FMILIB_BUILD_STATIC_LIB": "OFF" if self.options.shared else "ON",
                "FMILIB_BUILD_SHARED_LIB": "ON"  if self.options.shared else "OFF",
                "FMILIB_BUILD_TESTS": "OFF",
                "FMILIB_INSTALL_PREFIX": self.build_folder + "/install",
            })
        cmake.build()
        cmake.install()

    def package(self):
        fmilib_install_dir = self.build_folder + "/install"
        self.copy("*.h",    dst="include",  src=fmilib_install_dir+"/include")
        self.copy("*.dll",  dst="bin",      src=fmilib_install_dir, keep_path=False)
        self.copy("*.so",   dst="lib",      src=fmilib_install_dir, keep_path=False)
        self.copy("*.dylib",dst="lib",      src=fmilib_install_dir, keep_path=False)
        self.copy("*.lib",  dst="lib",      src=fmilib_install_dir, keep_path=False)
        self.copy("*.a",    dst="lib",      src=fmilib_install_dir, keep_path=False)
        self.copy("LICENSE.md",                  src="src", dst="licenses", keep_path=False)
        self.copy("FMILIB_Acknowledgements.txt", src="src", dst="licenses", keep_path=False)

    def package_info(self):
        if self.options.shared:
            self.cpp_info.libs = ["fmilib_shared"]
        else:
            self.cpp_info.libs = ["fmilib"]
