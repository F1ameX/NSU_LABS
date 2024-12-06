#pragma once

#include "parser_config.h"
#include "CSV_exceptions.h"
#include <iostream>
#include <fstream>
#include <tuple>
#include <sstream>
#include <vector>
#include <string>

template<typename... Types>
class CSVParser
{
public:
    CSVParser(std::istream& input_stream, size_t skip_lines = 0, const ParserConfig& config = {} );

    class Iterator
    {
    public:
        using iterator_category = std::input_iterator_tag;
        using value_type = std::tuple<Types...>;
        using difference_type = std::ptrdiff_t;
        using pointer = value_type*;
        using reference = value_type&;

        Iterator(std::istream* stream = nullptr, const ParserConfig& config = {}, size_t start_row = 0);
        Iterator(const Iterator& other);

        value_type operator*();
        Iterator& operator++();
        bool operator==(const Iterator& other) const;
        bool operator!=(const Iterator& other) const;

    private:
        std::istream* stream_;
        ParserConfig config_;
        size_t current_row_;
        std::string current_line_;
        value_type current_tuple_;

        value_type parse_line(const std::string& line);
        std::vector<std::string> tokenize(const std::string& line);

        template<std::size_t... Indices>
        value_type create_tuple_from_tokens(const std::vector<std::string>& tokens,
                                            std::index_sequence<Indices...>);

        template<typename T>
        static T convert_to_type(const std::string& token, size_t current_row);
    };

    Iterator begin();
    Iterator end();

private:
    std::istream& input_stream_;
    size_t skip_lines_;
    ParserConfig config_;
};