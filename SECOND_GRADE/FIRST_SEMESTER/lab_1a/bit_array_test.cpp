#include "bit_array.h"
#include "gtest/gtest.h"


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