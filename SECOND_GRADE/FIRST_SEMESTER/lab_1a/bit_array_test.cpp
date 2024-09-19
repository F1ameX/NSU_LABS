#include "bit_array.h"
#include "gtest/gtest.h"
#include <iostream>
#include <type_traits>


TEST(bitArrayTest, DefaultConstructor)
{
    BitArray bitArray;
    ASSERT_EQ(bitArray.size(), 0);
    ASSERT_TRUE(bitArray.empty());
}


TEST(bitArrayTest, SetAndStringBit)
{
    BitArray bitArray(5, 5);
    ASSERT_EQ(bitArray.to_string(), "00101");
    ASSERT_TRUE((std::is_same<decltype(bitArray.to_string()), std::string>::value));
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
    ASSERT_EQ(bitArray_2.size(), 2);
}


TEST(BitArrayTest, PushAndClearBit) {
    BitArray bitArray(8, 5);
    bitArray.push_back(true);

    ASSERT_TRUE(bitArray[8]);
    ASSERT_EQ(bitArray.size(), 9);

    bitArray.clear();

    ASSERT_EQ(bitArray.size(), 0);
    ASSERT_EQ(bitArray.to_string(), "");
}


TEST(BitArrayTest, SetAndAnalyzeBit)
{
    BitArray bitArray(5, 0);

    ASSERT_FALSE(bitArray.any());
    ASSERT_EQ(bitArray.count(), 0);

    bitArray.push_back(true);

    ASSERT_TRUE(bitArray.any());
    ASSERT_EQ(bitArray.count(), 1);

    bitArray.push_back(true);

    ASSERT_EQ(bitArray.count(), 2);

    bitArray.push_back(true);
    bitArray.push_back(true);

    ASSERT_EQ(bitArray.count(), 4);
}


TEST(BitArrayTest, SetAndCheckNoneBit)
{
    BitArray bitArray_1, bitArray_2(5, 5);

    ASSERT_TRUE(bitArray_1.none());
    ASSERT_FALSE(bitArray_2.none());
}


TEST(BitArrayTest, SetAndCompareBit)
{
    BitArray bitArray_1(5, 31), bitArray_2(5, 30);

    ASSERT_TRUE(bitArray_1 != bitArray_2);
    ASSERT_FALSE(bitArray_1 == bitArray_2);

    bitArray_2.set(0, true);

    ASSERT_TRUE(bitArray_1 == bitArray_2);
    ASSERT_FALSE(bitArray_1 != bitArray_2);
}


TEST(BitArrayTest, SetAndNegativeBit)
{
    BitArray bitArray(3, 5);

    ASSERT_EQ(bitArray.to_string(), "101");
    ASSERT_EQ((~bitArray).to_string(), "010");
}


TEST(BitArrayTest, SetAndEquateBit)
{
    BitArray bitArray_1(3, 5), bitArray_2;
    bitArray_2 = bitArray_1;
    ASSERT_TRUE(bitArray_1 == bitArray_2);
    ASSERT_EQ(bitArray_2.to_string(), "101");
}


TEST(BitArrayTest, SetAndBitwiseOpsBit)
{
    BitArray bitArray_1(3, 5), bitArray_2(3, 2), bitArray_3(4, 5);
    bitArray_1 &= bitArray_2;

    ASSERT_EQ(bitArray_1.to_string(), "000");
    ASSERT_THROW(bitArray_1 &= bitArray_3, std::invalid_argument);

    bitArray_1 = BitArray(3, 5);
    bitArray_1 |= bitArray_2;

    ASSERT_EQ(bitArray_1.to_string(), "111");
    ASSERT_THROW(bitArray_1 |= bitArray_3, std::invalid_argument);

    bitArray_2 = BitArray(3, 3);
    bitArray_1 ^= bitArray_2;

    ASSERT_EQ(bitArray_1.to_string(), "100");
    ASSERT_THROW(bitArray_1 ^= bitArray_3, std::invalid_argument);

    ASSERT_EQ((bitArray_1 & bitArray_2).to_string(), "000");
    ASSERT_EQ((bitArray_1 | bitArray_2).to_string(), "111");
    ASSERT_EQ((bitArray_1 ^ bitArray_2).to_string(), "111");
}


TEST(BitArrayTest, SetAndShiftBit)
{
        BitArray bitArray(8, 5);
        ASSERT_EQ(bitArray.to_string(), "00000101");

        BitArray shifted_left = bitArray << 2;
        ASSERT_EQ(shifted_left.to_string(), "00010100");

        BitArray shifted_right = bitArray >> 2;
        ASSERT_EQ(shifted_right.to_string(), "00000001");

        ASSERT_EQ((bitArray << 0).to_string(), bitArray.to_string());
        ASSERT_EQ((bitArray >> 0).to_string(), bitArray.to_string());

        BitArray bitArray_large_shift(8, 5);
        ASSERT_EQ((bitArray_large_shift << 8).to_string(), "00000000");
        ASSERT_EQ((bitArray_large_shift >> 8).to_string(), "00000000");

        BitArray bitArray_pattern(16, 0b1010101010101010);
        ASSERT_EQ(bitArray_pattern.to_string(), "1010101010101010");

        bitArray_pattern <<= 4;
        ASSERT_EQ(bitArray_pattern.to_string(), "1010101010100000");

        bitArray_pattern = BitArray(16, 0b1010101010101010);
        ASSERT_EQ(bitArray_pattern.to_string(), "1010101010101010");

        bitArray_pattern >>= 4;
        ASSERT_EQ(bitArray_pattern.to_string(), "0000101010101010");

        bitArray_pattern = BitArray(16, 0b1010101010101010);
        bitArray_pattern <<= 16;
        ASSERT_EQ(bitArray_pattern.to_string(), "0000000000000000");

        bitArray_pattern = BitArray(16, 0b1010101010101010);
        bitArray_pattern >>= 16;
        ASSERT_EQ(bitArray_pattern.to_string(), "0000000000000000");
}
