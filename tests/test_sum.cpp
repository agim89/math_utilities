#include <gtest/gtest.h>

#include "mylib/sum.h"

TEST(SumTest, Basic) { EXPECT_EQ(sum(2, 3), 5); }