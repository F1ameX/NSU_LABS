#pragma once

#include <iostream>
#include <fstream>


class FileManager {
public:
    static bool load_from_file(const std::string& filename, std::vector<std::vector<bool>>& field, std::string& universe_name, std::string& rule);
    static void save_to_file(const std::string& filename, const std::vector<std::vector<bool>>& grid, const std::string& universeName, const std::string& rule);
};