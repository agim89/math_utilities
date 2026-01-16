from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout

class MyLibConan(ConanFile):
    name = "mylib"
    version = None  # injected by CI
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "CMakeLists.txt", "src/*", "include/*", "tests/*"
    generators = "CMakeDeps", "CMakeToolchain"
    requires = "gtest/1.14.0"

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        cmake.test()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["mylib"]