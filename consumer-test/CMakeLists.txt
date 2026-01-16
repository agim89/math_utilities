cmake_minimum_required(VERSION 3.15)

project(consumer LANGUAGES CXX)

find_package(mylib REQUIRED CONFIG)

add_executable(consumer main.cpp)
target_link_libraries(consumer PRIVATE mylib::mylib)
