#include "CSV_parser.h"

template<typename... Types>
CSVParser<Types...>::CSVParser(std::istream& input_stream, size_t skip_lines, const ParserConfig& config)
        : input_stream_(input_stream), skip_lines_(skip_lines), config_(config)
{
    for (size_t i = 0; i < skip_lines_; ++i)
    {
        std::string dummy;
        std::getline(input_stream_, dummy);
    }
}


template<typename... Types>
typename CSVParser<Types...>::Iterator CSVParser<Types...>::begin() { return Iterator(&input_stream_, config_); }

template<typename... Types>
typename CSVParser<Types...>::Iterator CSVParser<Types...>::end() { return Iterator(); }

template<typename... Types>
CSVParser<Types...>::Iterator::Iterator(std::istream* stream, const ParserConfig& config, size_t start_row)
        : stream_(stream), config_(config), current_row_(start_row)
{
    if (stream_ && !stream_->eof())
    {
        std::getline(*stream_, current_line_);
        try
        {
            current_tuple_ = parse_line(current_line_);
        }
        catch (...)
        {
            ++(*this);
        }
    }
}

template<typename... Types>
typename CSVParser<Types...>::Iterator::value_type CSVParser<Types...>::Iterator::operator*() { return current_tuple_; }

template<typename... Types>
typename CSVParser<Types...>::Iterator& CSVParser<Types...>::Iterator::operator++()
{
    if (!stream_) return *this;

    while (stream_ && !stream_->eof())
    {
        ++current_row_;
        std::getline(*stream_, current_line_);

        try
        {
            current_tuple_ = parse_line(current_line_);
            return *this;
        }
        catch (const CSVFormatException& e)
        {
            std::cerr << "CSV Format Error at row " << e.row() + 1 << ", column " << e.column() + 1 << ": " << e.what() << std::endl;
            std::cerr << "Offending line: " << e.line() << std::endl;
        }
        catch (const std::exception& e)
        {
            std::cerr << "Error at row " << current_row_ << ": " << e.what() << std::endl;
        }
    }

    stream_ = nullptr;
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
    auto tokens = tokenize(line);
    if (tokens.size() != sizeof...(Types))
        throw CSVFormatException(current_row_, tokens.size(), "Column count mismatch", line);

    return create_tuple_from_tokens(tokens, std::index_sequence_for<Types...>{});
}

template<typename... Types>
std::vector<std::string> CSVParser<Types...>::Iterator::tokenize(const std::string& line)
{
    std::vector<std::string> tokens;
    std::string token;
    bool in_quotes = false;

    for (size_t i = 0; i < line.size(); ++i)
    {
        char c = line[i];

        if (c == config_.escape_character)
            in_quotes = !in_quotes;

        else if (c == config_.column_delimiter && !in_quotes)
        {
            tokens.push_back(token);
            token.clear();
        }
        else
            token += c;
    }

    if (in_quotes)
        throw CSVFormatException(current_row_, tokens.size(), "Unclosed quote in line", line);

    tokens.push_back(token);
    return tokens;
}

template<typename... Types>
template<std::size_t... Indices>
typename CSVParser<Types...>::Iterator::value_type
CSVParser<Types...>::Iterator::create_tuple_from_tokens(const std::vector<std::string>& tokens, std::index_sequence<Indices...>)
{
    return std::make_tuple(convert_to_type<Types>(tokens[Indices], current_row_)...);
}

template<typename... Types>
template<typename T>
T CSVParser<Types...>::Iterator::convert_to_type(const std::string& token, size_t current_row)
{
    if (token.empty())
    {
        if constexpr (std::is_arithmetic_v<T>)
            return T();
        else if constexpr (std::is_same_v<T, std::string>)
            return "";
        else
            throw CSVFormatException(current_row, 0, "Empty token is not convertible to this type", token);
    }

    if constexpr (std::is_same_v<T, std::string>)
        return token;
    else
    {
        T value;
        std::istringstream token_stream(token);
        token_stream >> value;

        if (token_stream.fail() || !token_stream.eof())
            throw CSVFormatException(current_row, 0, "Failed to convert token to type: " + token, token);

        return value;
    }
}

template class CSVParser<int, std::string, double>;