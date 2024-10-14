#pragma once

#include <iostream>
#include <fstream>

class FileManager {
private:
    std::ifstream input_file;
    std::ofstream output_file;
public:
    FileManager();
    ~FileManager();

    void load_from_file(const std::string& input_file_path);
    void save_to_file(const std::string& output_file_path);

};



