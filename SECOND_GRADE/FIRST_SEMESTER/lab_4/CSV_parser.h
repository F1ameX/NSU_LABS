#pragma once

#include <iostream>
#include <fstream>
#include <tuple>
#include <sstream>
#include <iterator>
#include <stdexcept>
#include <string>
#include <vector>


template<typename... Types>
class CSVParser
{
public:
    CSVParser(std::istream& input_stream, size_t skip_lines = 0);

    class Iterator;
    Iterator begin();
    Iterator end();

private:
    std::istream& input_stream_;
    size_t skip_lines_;
};


template<typename... Types>
class CSVParser<Types...>::Iterator
{
public:
    using iterator_category = std::input_iterator_tag;
    using value_type = std::tuple<Types...>;
    using difference_type = std::ptrdiff_t;
    using pointer = value_type*;
    using reference = value_type&;

    Iterator(std::istream* stream = nullptr);
    Iterator(const Iterator& other);

    value_type operator*();
    Iterator& operator++();
    bool operator==(const Iterator& other) const;
    bool operator!=(const Iterator& other) const;

private:
    std::istream* stream_;
    std::string current_line_;
    value_type current_tuple_;
    value_type parse_line(const std::string& line);
};