#pragma once

#include <iostream>
#include <list>
#include <map>
#include <fstream>
#include <algorithm>
#include <regex>

class WordData{
private:
    int words_counter = 0;
    std::list<std::string> input_file_strings;
    std::map<std::string, int> words_map;

public:
    int get_words_counter() const;
    const std::map<std::string, int>& get_words_map() const;
    void read_from_file(const std::string& input_file_name);
    void get_data_from_file();
    void process_file(const std::string& input_file_name);
};
