import os, pathlib

from conan import ConanFile
from conan.tools.apple import to_apple_arch
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import Environment
from conan.tools.files import patch, copy
from conan.tools.scm import Git


class FMILibraryConan(ConanFile):
    name = "fmilibrary"
    version = "3.0.4"
    license = "https://github.com/modelon-community/fmi-library/blob/master/LICENSE.md"
    url = "https://github.com/open-simulation-platform/conan-fmilibrary"
    description = "An implementation of the FMI standard which enables FMU import in applications"
    
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": False}

    tool_requires = "cmake/[>=3.15]"
    generators = "CMakeDeps"

    def source(self):
        git = Git(self)
        git.clone(url="https://github.com/modelon-community/fmi-library.git", target="src", args=["--branch=3.0.4"])

    def layout(self):
        cmake_layout(self)

    def generate(self):       
        tc = CMakeToolchain(self)
        tc.cache_variables["FMILIB_BUILD_STATIC_LIB"] = not self.options.shared
        tc.cache_variables["FMILIB_BUILD_SHARED_LIB"] = not not self.options.shared
        tc.cache_variables["FMILIB_BUILD_TESTS"] = False
        tc.cache_variables["FMILIB_GENERATE_DOXYGEN_DOC"] = False
        tc.cache_variables["FMILIB_INSTALL_PREFIX"] = pathlib.Path(os.path.join(self.build_folder, "install")).as_posix()
        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            # FMI 2.0.4 reserves "darwin64" for 64-bit x86, and other platforms
            # use the FMI 3 platform tuple. fmi-library derives the FMI 2
            # folder from the pointer size only, so it would look in darwin64.
            tc.cache_variables["FMILIB_FMI2_PLATFORM"] = "aarch64-darwin"
        tc.generate()

        if self.settings.os == "Macos":
            # fmi-library builds its bundled zlib and expat as external
            # projects, which do not see our toolchain file. They do pick up
            # the target architecture from the environment, though, and
            # without it they are built for the host when cross-compiling.
            env = Environment()
            env.define("CMAKE_OSX_ARCHITECTURES", to_apple_arch(self))
            env.vars(self).save_script("conanbuild_osx_architectures")
    
    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder="src")
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "*.dll", os.path.join(self.build_folder, str(self.settings.build_type)), os.path.join(self.package_folder, "bin"))

    def package_info(self):
        if self.options.shared:
            self.cpp_info.libs = ["fmilib_shared"]
        else:
            self.cpp_info.libs = ["fmilib"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["shlwapi"]
