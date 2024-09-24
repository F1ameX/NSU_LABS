#include "bit_array.h"

static constexpr int BITS_PER_LONG = sizeof(unsigned long) * 8;

BitArray::BitArray() : num_bits(0) {}
BitArray::~BitArray() = default;
BitArray::BitArray(const BitArray& b) : data(b.data), num_bits(b.num_bits) {};
BitArray& BitArray::reset(int n) {return set(n, false);}

int BitArray::size() const {return num_bits;}
bool BitArray::empty() const {return num_bits == 0;}
bool operator==(const BitArray & a, const BitArray & b) {return a.size() == b.size() && a.data == b.data;}
bool operator!=(const BitArray & a, const BitArray & b) {return !(a == b);}
bool BitArray::none() const {return !any();}


BitArray::BitArray(int num_bits, unsigned long value) : num_bits(num_bits)
{
    data.resize((num_bits + BITS_PER_LONG - 1) / BITS_PER_LONG, 0);
    if (num_bits > 0 && !data.empty())
        data[0] = value;
}


void BitArray::swap(BitArray& b)
{
    std::swap(data, b.data);
    std::swap(num_bits, b.num_bits);
}


BitArray& BitArray::operator=(const BitArray& b)
{
    if (this != &b)
    {
        data = b.data;
        num_bits = b.num_bits;
    }
    return *this;
}


void BitArray::resize(int new_size, bool value)
{
    if (new_size < 0)
        throw std::invalid_argument("New size must be non-negative");

    std::vector<unsigned long> new_data((new_size + BITS_PER_LONG - 1) / BITS_PER_LONG, value ? ~0UL : 0);
    int copy_bits = std::min(num_bits, new_size);
    for (int i = 0; i < copy_bits; ++i)
        if ((*this)[i])
            new_data[i / BITS_PER_LONG] |= (1UL << (i % BITS_PER_LONG));

    data = std::move(new_data);
    num_bits = new_size;
}


void BitArray::clear()
{
    data.clear();
    num_bits = 0;
}


void BitArray::push_back(bool bit)
{
    resize(num_bits + 1);
    set(num_bits - 1, bit);
}


BitArray& BitArray::operator&=(const BitArray& b)
{
    if (num_bits != b.num_bits)
        throw std::invalid_argument("Bit arrays must be of the same size for bitwise operations");

    for (size_t i = 0; i < data.size(); ++i)
        data[i] &= b.data[i];

    return *this;
}


BitArray& BitArray::operator|=(const BitArray& b)
{
    if (num_bits != b.num_bits)
        throw std::invalid_argument("Bit arrays must be of the same size for bitwise operations");

    for (size_t i = 0; i < data.size(); ++i)
        data[i] |= b.data[i];

    return *this;
}


BitArray& BitArray::operator^=(const BitArray& b)
{
    if (num_bits != b.num_bits)
        throw std::invalid_argument("Bit arrays must be of the same size for bitwise operations");

    for (size_t i = 0; i < data.size(); ++i)
        data[i] ^= b.data[i];

    return *this;
}


BitArray& BitArray::operator<<=(int n)
{
    if (n < 0) return *this >>= -n;
    if (n >= num_bits)
    {
        reset();
        return *this;
    }

    int full_shifts = n / BITS_PER_LONG;
    int bit_shifts = n % BITS_PER_LONG;

    if (bit_shifts == 0)
        std::move(data.begin(), data.end() - full_shifts, data.begin() + full_shifts);
    else
    {
        for (int i = data.size() - 1; i > full_shifts; --i)
            data[i] = (data[i - full_shifts] << bit_shifts) |
                      (data[i - full_shifts - 1] >> (BITS_PER_LONG - bit_shifts));

        data[full_shifts] = data[0] << bit_shifts;
    }
    std::fill(data.begin(), data.begin() + full_shifts, 0);
    return *this;
}


BitArray& BitArray::operator>>=(int n)
{
    if (n < 0) return *this <<= -n;
    if (n >= num_bits)
    {
        reset();
        return *this;
    }
    int full_shifts = n / BITS_PER_LONG;
    int bit_shifts = n % BITS_PER_LONG;

    if (bit_shifts == 0)
        std::move(data.begin() + full_shifts, data.end(), data.begin());
    else
    {
        for (int i = 0; i < data.size() - full_shifts - 1; ++i)
            data[i] = (data[i + full_shifts] >> bit_shifts) |
                      (data[i + full_shifts + 1] << (BITS_PER_LONG - bit_shifts));

        data[data.size() - full_shifts - 1] = data.back() >> bit_shifts;
    }
    std::fill(data.end() - full_shifts, data.end(), 0);
    return *this;
}


BitArray BitArray::operator<<(int n) const
{
    BitArray result(*this);
    return result <<= n;
}


BitArray BitArray::operator>>(int n) const
{
    BitArray result(*this);
    return result >>= n;
}


BitArray& BitArray::set(int n, bool val)
{
    if (n < 0 || n >= num_bits)
        throw std::out_of_range("Bit index out of range");

    if (val)
        data[n / BITS_PER_LONG] |= (1UL << (n % BITS_PER_LONG));
    else
        data[n / BITS_PER_LONG] &= ~(1UL << (n % BITS_PER_LONG));

    return *this;
}


BitArray& BitArray::set()
{
    std::fill(data.begin(), data.end(), ~0UL);
    return *this;
}


BitArray& BitArray::reset()
{
    std::fill(data.begin(), data.end(), 0);
    return *this;
}


bool BitArray::any() const
{
    for (const auto& chunk : data)
        if (chunk != 0)
            return true;
    return false;
}


BitArray BitArray::operator~() const
{
    BitArray result(*this);
    for (auto& chunk : result.data)
        chunk = ~chunk;
    return result;
}


int BitArray::count() const
{
    int count = 0;
    for (const auto& chunk : data)
        count += __builtin_popcountl(chunk);
    return count;
}


bool BitArray::operator[](int i) const
{
    if (i < 0 || i >= num_bits)
        throw std::out_of_range("Bit index out of range");
    return data[i / BITS_PER_LONG] & (1UL << (i % BITS_PER_LONG));
}


std::string BitArray::to_string() const
{
    std::string result;
    for (int i = num_bits - 1; i >= 0; --i)
        result += (*this)[i] ? '1' : '0';
    return result;
}


BitArray operator&(const BitArray& b1, const BitArray& b2)
{
    BitArray result(b1);
    result &= b2;
    return result;
}


BitArray operator|(const BitArray& b1, const BitArray& b2)
{
    BitArray result(b1);
    result |= b2;
    return result;
}


BitArray operator^(const BitArray& b1, const BitArray& b2)
{
    BitArray result(b1);
    result ^= b2;
    return result;
}


BitArray::Iterator BitArray::begin() const {return Iterator(this, 0);}
BitArray::Iterator BitArray::end() const {return Iterator(this, num_bits - 1);}
BitArray::Iterator::Iterator(const BitArray* ba, int idx) : bit_array(ba), index(idx) {}
bool BitArray::Iterator::operator*() const {return (*bit_array)[index];}
bool BitArray::Iterator::operator!=(const BitArray::Iterator& other) const { return index != other.index;}
bool BitArray::Iterator::operator==(const BitArray::Iterator& other) const{ return index == other.index;}

BitArray::Iterator& BitArray::Iterator::operator++()
{
    ++index;
    return *this;
}
