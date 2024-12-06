#include "csv_parser.h"
#include "tuple_printer.h"
#include <gtest/gtest.h>
#include <sstream>

TEST(CSVParserTest, EmptyFile)
{
    std::istringstream empty_stream("");
    CSVParser<int, std::string, double> parser(empty_stream, 0);
    EXPECT_EQ(parser.begin(), parser.end());
}


TEST(CSVParserTest, NormalData)
{
    std::istringstream data("id,name,value\n1,John,3.14\n2,Alice,42.0\n");
    CSVParser<int, std::string, double> parser(data, 1);
    auto it = parser.begin();
    EXPECT_EQ(*it, std::make_tuple(1, "John", 3.14));
    ++it;
    EXPECT_EQ(*it, std::make_tuple(2, "Alice", 42.0));
}


TEST(CSVParserTest, EscapedValues)
{
    std::istringstream data("id,name,value\n1,\"Alice, Smith\",42.0\n");
    CSVParser<int, std::string, double> parser(data, 1);
    auto it = parser.begin();
    EXPECT_EQ(*it, std::make_tuple(1, "Alice, Smith", 42.0));
}


TEST(CSVParserTest, UnclosedQuote)
{
    std::istringstream data("id,name,value\n1,\"Unclosed,42.0\n2,Valid,3.14\n");
    CSVParser<int, std::string, double> parser(data, 1);

    auto it = parser.begin();
    EXPECT_EQ(*it, std::make_tuple(2, "Valid", 3.14));
}


TEST(CSVParserTest, EmptyValues)
{
    std::istringstream data("id,name,value\n1,,3.14\n,John,42.0\n");
    CSVParser<int, std::string, double> parser(data, 1);
    auto it = parser.begin();
    EXPECT_EQ(*it, std::make_tuple(1, "", 3.14));
    ++it;
    EXPECT_EQ(*it, std::make_tuple(0, "John", 42.0));
}


TEST(CSVParserTest, TypeConversionError)
{
    std::istringstream data("id,name,value\n1,John,not_a_number\n2,Alice,42.0\n");
    CSVParser<int, std::string, double> parser(data, 1);

    auto it = parser.begin();
    EXPECT_EQ(*it, std::make_tuple(2, "Alice", 42.0));
}