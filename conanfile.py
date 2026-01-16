from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.files import copy
import os

class MyLibConan(ConanFile):
    name = "mylib"
    version = os.getenv("CONAN_VERSION", "0.0.0")
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "CMakeLists.txt", "src/*", "include/*", "tests/*", "cmake/*"
    generators = "CMakeDeps", "CMakeToolchain"
    requires = "gtest/1.14.0"

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        # Pass PROJECT_VERSION via CMake cache variable
        cmake.configure(variables={"PROJECT_VERSION": self.version})
        cmake.build()
        cmake.test()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["mylib"]
        self.cpp_info.set_property("cmake_find_mode", "config")