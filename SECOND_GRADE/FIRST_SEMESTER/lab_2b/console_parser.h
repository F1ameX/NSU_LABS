#pragma once
#include <iostream>


class ConsoleParser {
private:
    bool help_requested_ = false;
    bool mode;
    std::size_t iterations;
    std::string input_file;
    std::string output_file;

public:
    ConsoleParser();
    bool parse(int argc, char* argv[]);
    static void get_help();
    bool help_requested() const;
    [[nodiscard]]std::size_t get_iterations() const;
    [[nodiscard]]bool is_offline_mode() const;
    [[nodiscard]]std::string get_input_file() const;
    [[nodiscard]]std::string get_output_file() const;
};