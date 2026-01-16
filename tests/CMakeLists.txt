find_package(GTest REQUIRED)

add_executable(test_sum test_sum.cpp)
target_link_libraries(test_sum PRIVATE mylib GTest::gtest_main)

add_test(NAME sum_test COMMAND test_sum)