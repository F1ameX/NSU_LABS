#include "CSV_parser.h"
#include "tuple_printer.h"
#include <fstream>
#include <iostream>

int main()
{
    std::ifstream file("test.csv");

    ParserConfig config;
    config.column_delimiter = ',';
    config.escape_character = '"';

    try
    {
        CSVParser<int, std::string, double> parser(file, 1, config);
        for (const auto& row : parser)
            std::cout << row << std::endl;
    }
    catch (const std::exception& e)
    {
        std::cerr << "Error: " << e.what() << std::endl;
    }

    return 0;
}