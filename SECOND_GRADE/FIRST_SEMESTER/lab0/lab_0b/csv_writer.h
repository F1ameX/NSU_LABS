#include <iostream>
#include <fstream>
#include <map>

class CSVWriter {
public:
    static void write_to_file(const std::string& output_file_name, const std::map<std::string, int>& words_map, int words_quantity);
};