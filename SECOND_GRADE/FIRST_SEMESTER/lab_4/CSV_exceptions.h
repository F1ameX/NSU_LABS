#pragma once

#include <stdexcept>
#include <string>

class CSVFormatException : public std::runtime_error
{
public:
    CSVFormatException(size_t row, size_t column, const std::string& message, const std::string& line = "")
            : std::runtime_error(message), row_(row), column_(column), line_(line) {}

    [[nodiscard]] size_t row() const { return row_; }
    [[nodiscard]] size_t column() const { return column_; }
    [[nodiscard]] const std::string& line() const { return line_; }

private:
    size_t row_;
    size_t column_;
    std::string line_;
};
