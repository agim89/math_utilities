cmake_minimum_required(VERSION 3.15)

project(mylib VERSION 1.1.1 LANGUAGES CXX)

# Get full version from Conan env (if set)
if(DEFINED ENV{CONAN_PACKAGE_VERSION})
    set(MYLIB_VERSION_FULL "$ENV{CONAN_PACKAGE_VERSION}")
else()
    set(MYLIB_VERSION_FULL "${PROJECT_VERSION}")
endif()

message(STATUS "Building ${PROJECT_NAME} ${MYLIB_VERSION_FULL}")

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Library target
add_library(mylib src/mylib.cpp)
target_include_directories(mylib
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)

# Set library output name
set_target_properties(mylib PROPERTIES
    OUTPUT_NAME mylib
    VERSION ${PROJECT_VERSION}
    SOVERSION ${PROJECT_VERSION_MAJOR}
)

# Installation rules
include(GNUInstallDirs)

install(TARGETS mylib
    EXPORT mylibTargets
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)

install(DIRECTORY include/
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

# Export targets
install(EXPORT mylibTargets
    FILE mylibTargets.cmake
    NAMESPACE mylib::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/mylib
)

# Generate and install Config file
include(CMakePackageConfigHelpers)

configure_package_config_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake/mylibConfig.cmake.in"
    "${CMAKE_CURRENT_BINARY_DIR}/mylibConfig.cmake"
    INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/mylib
)

write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/mylibConfigVersion.cmake"
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
)

install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/mylibConfig.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/mylibConfigVersion.cmake"
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/mylib
)

# Testing
if(BUILD_TESTING)
    enable_testing()
    add_subdirectory(tests)
endif()