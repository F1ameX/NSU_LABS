#include "file_manager.h"

FileManager::FileManager() = default;


FileManager::~FileManager()
{
    if (input_file.is_open()) input_file.close();
    if (output_file.is_open()) input_file.close();
}


void FileManager::load_from_file(const std::string &input_file_path)
{
    input_file.open(input_file_path);
    if (!input_file)
    {
        std::cerr << "Error! Unable to open input file: " << input_file_path << std::endl;
        return;
    }
}


void FileManager::save_to_file(const std::string &output_file_path)
{
    output_file.open(output_file_path);
    if (!output_file)
    {
        std::cerr << "Error! Unable to open output file: " << output_file_path << std::endl;
        return;
    }
}