#include "bit_array.h"
#include "gtest/gtest.h"
#include <iostream>

TEST(bitArrayTest, DefaultConstructor)
{
    BitArray bitArray;
    ASSERT_EQ(bitArray.size(), 0);
    ASSERT_TRUE(bitArray.empty());
}


TEST(BitArrayTest, ConstructorWithValue)
{
    BitArray bitArray(10, 5);
    ASSERT_EQ(bitArray.size(), 10);
    ASSERT_EQ(bitArray.to_string().substr(7), "101");
}


TEST(BitArrayTest, SetAndGetBit)
{
    BitArray bitArray(5, 0);
    bitArray.set(1, true);
    ASSERT_TRUE(bitArray[1]);
    ASSERT_FALSE(bitArray[0]);
}


TEST(BitArrayTest, RestAndCheckBit)
{
    BitArray bitArray(8, 255);
    ASSERT_EQ(bitArray.size(), 8);
    ASSERT_EQ(bitArray.to_string(), "11111111");

    bitArray.reset(2);
    ASSERT_FALSE(bitArray[2]);

    bitArray.reset();
    ASSERT_FALSE(bitArray[0]);
}


TEST(BitArrayTest, SwapAndResizeBit)
{
    BitArray bitArray_1(10, 255);
    BitArray bitArray_2(10, 5);

    bitArray_1.swap(bitArray_2);

    ASSERT_EQ(bitArray_1.to_string().substr(7), "101");
    ASSERT_EQ(bitArray_2.to_string().substr(2, 8), "11111111");

    bitArray_1.resize(8, false);
    bitArray_2.resize(2, true);

    ASSERT_EQ(bitArray_1.to_string().substr(5), "101");
    ASSERT_EQ(bitArray_2.to_string(), "11");
}
