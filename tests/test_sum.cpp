#include <gtest/gtest.h>

#include "mylib/mylib.h"

TEST(MylibTest, SumPositive) {
    EXPECT_EQ(mylib::sum(2, 3), 5);
    EXPECT_EQ(mylib::sum(10, 20), 30);
}

TEST(MylibTest, SumNegative) {
    EXPECT_EQ(mylib::sum(-5, -3), -8);
    EXPECT_EQ(mylib::sum(-10, 10), 0);
}

TEST(MylibTest, SumZero) {
    EXPECT_EQ(mylib::sum(0, 0), 0);
    EXPECT_EQ(mylib::sum(5, 0), 5);
}

TEST(MylibTest, MultiplyPositive) {
    EXPECT_EQ(mylib::multiply(2, 3), 6);
    EXPECT_EQ(mylib::multiply(10, 5), 50);
}

TEST(MylibTest, MultiplyNegative) {
    EXPECT_EQ(mylib::multiply(-2, 3), -6);
    EXPECT_EQ(mylib::multiply(-5, -4), 20);
}

TEST(MylibTest, MultiplyZero) {
    EXPECT_EQ(mylib::multiply(0, 5), 0);
    EXPECT_EQ(mylib::multiply(100, 0), 0);
}