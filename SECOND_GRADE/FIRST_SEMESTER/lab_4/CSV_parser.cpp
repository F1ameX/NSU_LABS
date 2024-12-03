#include "CSV_parser.h"
#include <tuple>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>


template<typename... Types>
CSVParser<Types...>::CSVParser(std::istream& input_stream, size_t skip_lines) : input_stream_(input_stream), skip_lines_(skip_lines)
{
    for (size_t i = 0; i < skip_lines_; ++i)
    {
        std::string dummy;
        std::getline(input_stream_, dummy);
    }
}


template<typename... Types>
typename CSVParser<Types...>::Iterator CSVParser<Types...>::begin() { return Iterator(&input_stream_); }

template<typename... Types>
typename CSVParser<Types...>::Iterator CSVParser<Types...>::end() { return Iterator(); }

template<typename... Types>
CSVParser<Types...>::Iterator::Iterator(std::istream* stream) : stream_(stream)
{
    if (stream_ && !stream_->eof())
    {
        std::getline(*stream_, current_line_);
        current_tuple_ = parse_line(current_line_);
    }
}


template<typename... Types>
CSVParser<Types...>::Iterator::Iterator(const Iterator& other)
        : stream_(other.stream_),
          current_line_(other.current_line_),
          current_tuple_(other.current_tuple_) {}


template<typename... Types>
typename CSVParser<Types...>::Iterator::value_type
CSVParser<Types...>::Iterator::operator*() { return current_tuple_; }


template<typename... Types>
typename CSVParser<Types...>::Iterator&
CSVParser<Types...>::Iterator::operator++()
{
    if (stream_ && !stream_->eof())
    {
        std::getline(*stream_, current_line_);
        if (!current_line_.empty())
            current_tuple_ = parse_line(current_line_);
        else
            stream_ = nullptr;
    }
    return *this;
}


template<typename... Types>
bool CSVParser<Types...>::Iterator::operator==(const Iterator& other) const { return stream_ == other.stream_; }

template<typename... Types>
bool CSVParser<Types...>::Iterator::operator!=(const Iterator& other) const { return !(*this == other); }

template<typename... Types>
typename CSVParser<Types...>::Iterator::value_type
CSVParser<Types...>::Iterator::parse_line(const std::string& line)
{
    std::istringstream line_stream(line);
    std::vector<std::string> tokens;
    std::string token;
    while (std::getline(line_stream, token, ','))
        tokens.push_back(token);

    if (tokens.size() != sizeof...(Types))
        throw std::runtime_error("Column count mismatch in CSV line");

    return create_tuple_from_tokens(tokens, std::index_sequence_for<Types...>{});
}


template<typename... Types>
template<std::size_t... Indices>
typename CSVParser<Types...>::Iterator::value_type
CSVParser<Types...>::Iterator::create_tuple_from_tokens(
        const std::vector<std::string>& tokens,
        std::index_sequence<Indices...>) { return std::make_tuple(convert_to_type<Types>(tokens[Indices])...); }


template<typename T>
T convert_to_type(const std::string& token)
{
    T value;
    std::istringstream token_stream(token);
    token_stream >> value;
    if (token_stream.fail())
        throw std::runtime_error("Failed to convert token to type");
    return value;
}