#pragma once

#include "cell.h"
#include <iostream>
#include <fstream>


class FileManager {
public:
    static bool load_from_file(const std::string& filename, std::vector<std::vector<Cell>>& field, std::string& universe_name, std::string& rule);
    static void save_to_file(const std::string& filename, const std::vector<std::vector<Cell>>& field, const std::string& universe_name, const std::string& rule);
};