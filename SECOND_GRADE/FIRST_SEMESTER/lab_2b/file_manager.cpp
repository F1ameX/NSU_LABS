#include "file_manager.h"
#include <iostream>


bool FileManager::load_from_file(const std::string& filename, std::vector<std::vector<bool>> &field, std::string &universe_name, std::string &rule)
{
    std::ifstream input_file(filename);
    if (!input_file.is_open())
    {
        std::cerr << "Can`t open file: " << filename << std::endl;
        return false;
    }

    int row = 0;
    bool name_found = false, rule_found = false;
    std::string line;

    while(getline(input_file, line))
    {
        if (line[0] == '#')
        {

            if (row == 0 && line.substr(1) != "Life 1.06")
            {
                std::cerr << "Wrong universe file format. Expected Life 1.06, received: " << line.substr(1) << std::endl;
                input_file.close();
                return false;
            }

            if (line[1] == 'N')
            {
                universe_name = line.substr(3);
                name_found = true;
            }

            if (line[1] == 'R')
            {
                rule = line.substr(3);
                rule_found = true;
            }
        }

        else
        {
            int x, y;
            if (sscanf(line.c_str(), "%d %d", &x, &y) == 2)
            {
                if (x >= 0 && y >= 0 && x < field.size() && y < field[0].size())
                    field[x][y] = true;

                else
                {
                    std::cerr << "Coordinates in file out of bounds: " << x << ", " << y << std::endl;
                    return false;
                }

            }

            else
            {
                std::cerr << "Invalid format for coordinates in file: " << line << std::endl;
                return false;
            }
        }
        row++;
    }
    input_file.close();

    if (!name_found)
        std::cerr << "Warning. No universe name found in the file." << std::endl;

    if (!rule_found)
        std::cerr << "Warning. No transition rule found in the file." << std::endl;

    return true;
}


void FileManager::save_to_file(const std::string& filename, const std::vector<std::vector<bool>>& field, const std::string& universe_name, const std::string& rule)
{
    std::ofstream output_file(filename);

    if (!output_file.is_open())
    {
        std::cerr << "Can`t open file: " << filename << std::endl;
        return;
    }

    output_file << "#Life 1.06" << std::endl;
    output_file << "#N " << universe_name << std::endl;
    output_file << "#R " << rule << std::endl;

    for (size_t y = 0; y < field.size(); y++)
        for(size_t x = 0; x < field[y].size(); x++)
            if (field[y][x])
                output_file << x << ' ' << y << std::endl;

    output_file.close();
}
