cmake_minimum_required(VERSION 3.15)

# Allow version to be passed via -DPROJECT_VERSION=... or default to 0.0.0
if(NOT DEFINED PROJECT_VERSION)
    set(PROJECT_VERSION "0.0.0")
endif()

project(mylib VERSION ${PROJECT_VERSION} LANGUAGES CXX)

add_library(mylib src/sum.cpp)
target_include_directories(mylib
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)

include(GNUInstallDirs)

install(TARGETS mylib
    EXPORT mylibTargets
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(DIRECTORY include/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

install(EXPORT mylibTargets
    FILE mylibConfig.cmake
    NAMESPACE mylib::
    DESTINATION lib/cmake/mylib
)

enable_testing()
add_subdirectory(tests)
