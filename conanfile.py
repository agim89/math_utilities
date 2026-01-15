from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import copy
import os
import subprocess


class MylibConan(ConanFile):
    name = "mylib"
    version = "1.1.1"
    license = "MIT"
    author = "Dmitri Telinov <Dmitri.Telinov@avenga.com>"
    url = "https://github.com/dmitritelinov/mylib"
    description = "A trivial C++ library for CI/CD demonstration"
    topics = ("example", "library")
    
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }
    
    exports_sources = "CMakeLists.txt", "src/*", "include/*", "cmake/*"
    
    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
    
    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
    
    def layout(self):
        cmake_layout(self)
    
    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = "OFF"
        tc.generate()
        
        deps = CMakeDeps(self)
        deps.generate()
    
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
    
    def package(self):
        cmake = CMake(self)
        cmake.install()
        
    def package_info(self):
        self.cpp_info.libs = ["mylib"]
        self.cpp_info.set_property("cmake_file_name", "mylib")
        self.cpp_info.set_property("cmake_target_name", "mylib::mylib")
        
        # For legacy generators
        self.cpp_info.names["cmake_find_package"] = "mylib"
        self.cpp_info.names["cmake_find_package_multi"] = "mylib"
    def set_version(self):
        try:
            short_sha = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'])
            short_sha = short_sha.decode().strip()
            self.version = f"1.1.1-dev-{short_sha}"
        except subprocess.CalledProcessError:
            self.version = "1.1.1-dev-unknown"