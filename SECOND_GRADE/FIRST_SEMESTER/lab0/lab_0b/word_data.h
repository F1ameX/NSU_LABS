#pragma once

#include <iostream>
#include <list>
#include <map>
#include <fstream>
#include <algorithm>
#include <regex>

class WordData{
private:
    std::map<std::string, int> words_map;

public:
    [[nodiscard]] const std::map<std::string, int>& get_words_map() const;
    void process_file_data(const std::string& input_file_name);
};
