import os, pathlib

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import patch, copy
from conan.tools.scm import Git


class FMILibraryConan(ConanFile):
    name = "fmilibrary"
    version = "2.3"
    license = "https://github.com/modelon-community/fmi-library/blob/master/LICENSE.md"
    url = "https://github.com/open-simulation-platform/conan-fmilibrary"
    description = "An implementation of the FMI standard which enables FMU import in applications"
    
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": False}

    generators = "CMakeDeps"

    exports_sources = "build-static-c99snprintf.patch"

    def source(self):
        git = Git(self)
        git.clone(url="https://github.com/modelon-community/fmi-library.git", target="src", args=["--branch=2.3"])
        patch(self, base_path="src", patch_file="build-static-c99snprintf.patch")

    def layout(self):
        cmake_layout(self)

    def generate(self):       
        tc = CMakeToolchain(self)
        tc.cache_variables["FMILIB_BUILD_STATIC_LIB"] = False if self.options.shared else True
        tc.cache_variables["FMILIB_BUILD_SHARED_LIB"] = True if self.options.shared else False
        tc.cache_variables["FMILIB_BUILD_TESTS"] = False
        tc.cache_variables["FMILIB_INSTALL_PREFIX"] = pathlib.Path(os.path.join(self.build_folder, "install")).as_posix()
        tc.generate()
    
    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder="src")
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "*.dll", os.path.join(self.build_folder, "Debug"), os.path.join(self.package_folder, "bin"))
        copy(self, "*.dll", os.path.join(self.build_folder, "Release"), os.path.join(self.package_folder, "bin"))

    def package_info(self):
        if self.options.shared:
            self.cpp_info.libs = ["fmilib_shared"]
        else:
            self.cpp_info.libs = ["fmilib"]
