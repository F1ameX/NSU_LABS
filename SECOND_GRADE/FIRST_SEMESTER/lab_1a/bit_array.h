#include <iostream>
#include <vector>
#include <stdexcept>
#include <algorithm>
#include <string>

/**
 * @class BitArray
 * @brief A dynamic array of bits that allows bitwise operations and resizing.
 *
 * This class provides a flexible bit array, supporting bitwise operations, dynamic resizing,
 * and memory-efficient storage of bits. It can be used for various applications such as
 * bit manipulation tasks, set representation, and more.
 */
class BitArray {
private:
    int num_bits;  ///< Number of bits in the array
    std::vector<unsigned long> data;  ///< Underlying storage for the bit array

public:
    /**
     * Default constructor.
     * Initializes an empty bit array.
     */
    BitArray();

    /**
     * Destructor.
     * Releases any allocated memory.
     */
    ~BitArray();

    /**
     * Constructs a bit array of the specified size.
     * Optionally initializes the first bits with a provided value.
     * @param num_bits The number of bits in the array.
     * @param value The initial value for the first bits (optional).
     */
    explicit BitArray(int num_bits, unsigned long value = 0);

    /**
     * Copy constructor.
     * Creates a copy of an existing bit array.
     * @param b The bit array to copy.
     */
    BitArray(const BitArray& b);

    /**
     * Swaps the contents of this bit array with another.
     * @param b The other bit array to swap with.
     */
    void swap(BitArray& b);

    /**
     * Assignment operator.
     * Assigns another bit array to this one.
     * @param b The bit array to assign.
     * @return Reference to this bit array.
     */
    BitArray& operator=(const BitArray& b);

    /**
     * Resizes the bit array to the new size.
     * Newly added bits will be initialized to the given value.
     * @param num_bits The new size of the bit array.
     * @param value The value to initialize new bits with.
     * @throws std::invalid_argument if the new size is negative.
     */
    void resize(int num_bits, bool value = false);

    /**
     * Clears the bit array, removing all bits.
     */
    void clear();

    /**
     * Adds a new bit to the end of the array.
     * Resizes the array if necessary.
     * @param bit The bit to add.
     */
    void push_back(bool bit);

    /**
     * Bitwise AND operation.
     * Modifies this array by applying a bitwise AND with another bit array.
     * Both arrays must be of the same size.
     * @param b The other bit array to AND with.
     * @return Reference to this bit array.
     * @throws std::invalid_argument if the arrays have different sizes.
     */
    BitArray& operator&=(const BitArray& b);

    /**
     * Bitwise OR operation.
     * Modifies this array by applying a bitwise OR with another bit array.
     * Both arrays must be of the same size.
     * @param b The other bit array to OR with.
     * @return Reference to this bit array.
     * @throws std::invalid_argument if the arrays have different sizes.
     */
    BitArray& operator|=(const BitArray& b);

    /**
     * Bitwise XOR operation.
     * Modifies this array by applying a bitwise XOR with another bit array.
     * Both arrays must be of the same size.
     * @param b The other bit array to XOR with.
     * @return Reference to this bit array.
     * @throws std::invalid_argument if the arrays have different sizes.
     */
    BitArray& operator^=(const BitArray& b);

    /**
     * Left shift operation.
     * Shifts all bits in the array to the left by the given number of positions.
     * Zeroes are shifted into the empty spaces.
     * @param n The number of positions to shift.
     * @return Reference to this bit array.
     */
    BitArray& operator<<=(int n);

    /**
     * Right shift operation.
     * Shifts all bits in the array to the right by the given number of positions.
     * Zeroes are shifted into the empty spaces.
     * @param n The number of positions to shift.
     * @return Reference to this bit array.
     */
    BitArray& operator>>=(int n);

    /**
     * Left shift operation (const version).
     * Returns a new bit array with bits shifted left by the given number of positions.
     * Zeroes are shifted into the empty spaces.
     * @param n The number of positions to shift.
     * @return A new bit array shifted to the left.
     */
    BitArray operator<<(int n) const;

    /**
     * Right shift operation (const version).
     * Returns a new bit array with bits shifted right by the given number of positions.
     * Zeroes are shifted into the empty spaces.
     * @param n The number of positions to shift.
     * @return A new bit array shifted to the right.
     */
    BitArray operator>>(int n) const;

    /**
     * Sets the bit at the specified index to the given value.
     * @param n The index of the bit to set.
     * @param val The value to set the bit to (true for 1, false for 0).
     * @return Reference to the current BitArray object.
     * @throws std::out_of_range if the index is out of bounds.
     */
    BitArray& set(int n, bool val = true);

    /**
     * Sets all bits in the array to 1 (true).
     * @return Reference to the current BitArray object.
     */
    BitArray& set();

    /**
     * Resets the bit at the specified index to 0 (false).
     * @param n The index of the bit to reset.
     * @return Reference to the current BitArray object.
     * @throws std::out_of_range if the index is out of bounds.
     */
    BitArray& reset(int n);

    /**
     * Resets all bits in the array to 0 (false).
     * @return Reference to the current BitArray object.
     */
    BitArray& reset();

    /**
     * Checks if any bits in the array are set to 1.
     * @return true if at least one bit is set to 1, false otherwise.
     */
    [[nodiscard]]bool any() const;

    /**
     * Checks if all bits in the array are 0.
     * @return true if all bits are 0, false otherwise.
     */
    [[nodiscard]]bool none() const;

    /**
     * Bitwise NOT operation.
     * Returns a new bit array with all bits inverted (0 becomes 1, and 1 becomes 0).
     * @return A new bit array with inverted bits.
     */
    BitArray operator~() const;

    /**
     * Counts the number of bits set to 1 in the array.
     * @return The number of bits set to 1.
     */
    [[nodiscard]]int count() const;

    /**
     * Accessor operator.
     * Returns the value of the bit at the specified index.
     * @param i The index of the bit to access.
     * @return The value of the bit at the specified index.
     * @throws std::out_of_range if the index is out of bounds.
     */
    bool operator[](int i) const;

    /**
     * Returns the size of the bit array (number of bits).
     * @return The number of bits in the array.
     */
    [[nodiscard]]int size() const;

    /**
     * Checks if the bit array is empty.
     * @return true if the bit array is empty, false otherwise.
     */
    [[nodiscard]]bool empty() const;

    /**
     * Returns a string representation of the bit array.
     * @return A string representing the bit array.
     */
    [[nodiscard]] std::string to_string() const;

    friend bool operator==(const BitArray &a, const BitArray &b);
    friend bool operator!=(const BitArray &a, const BitArray &b);
};

/**
 * Equality operator.
 * Checks if two bit arrays are equal.
 * @param a The first bit array.
 * @param b The second bit array.
 * @return true if the arrays are equal, false otherwise.
 */
bool operator==(const BitArray & a, const BitArray & b);

/**
 * Inequality operator.
 * Checks if two bit arrays are not equal.
 * @param a The first bit array.
 * @param b The second bit array.
 * @return true if the arrays are not equal, false otherwise.
 */
bool operator!=(const BitArray & a, const BitArray & b);

/**
 * Bitwise AND operator.
 * Returns a new bit array that is the result of bitwise AND between two arrays.
 * @param b1 The first bit array.
 * @param b2 The second bit array.
 * @return A new bit array that is the result of b1 & b2.
 */
BitArray operator&(const BitArray& b1, const BitArray& b2);

/**
 * Bitwise OR operator.
 * Returns a new bit array that is the result of bitwise OR between two arrays.
 * @param b1 The first bit array.
 * @param b2 The second bit array.
 * @return A new bit array that is the result of b1 | b2.
 */
BitArray operator|(const BitArray& b1, const BitArray& b2);

/**
 * Bitwise XOR operator.
 * Returns a new bit array that is the result of bitwise XOR between two arrays.
 * @param b1 The first bit array.
 * @param b2 The second bit array.
 * @return A new bit array that is the result of b1 ^ b2.
 */
BitArray operator^(const BitArray& b1, const BitArray& b2);

