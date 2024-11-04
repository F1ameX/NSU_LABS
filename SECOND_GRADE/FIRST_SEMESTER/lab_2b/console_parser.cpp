#include "console_parser.h"

ConsoleParser::ConsoleParser() : iterations(0), mode(false), input_file("none"), output_file("none") {}
bool ConsoleParser::is_offline_mode() const { return mode; }
bool ConsoleParser::help_requested() const { return help_requested_; }
std::size_t ConsoleParser::get_iterations() const { return iterations; }
std::string ConsoleParser::get_input_file() const { return input_file; }
std::string ConsoleParser::get_output_file() const { return output_file; }


bool ConsoleParser::parse(int argc, char* argv[])
{
    for (int i = 1; i < argc; i++)
    {
        if (strcmp(argv[i], "-f") == 0 || strcmp(argv[i], "--file") == 0)
        {
            if (i + 1 < argc)
                input_file = std::string(argv[++i]);
            else
            {
                std::cerr << "Error: No input filename provided. Use -h or --help for usage." << std::endl;
                return false;
            }
        }
        else if (strcmp(argv[i], "-o") == 0 || strcmp(argv[i], "--output") == 0)
        {
            if (i + 1 < argc)
                output_file = std::string(argv[++i]);
            else
            {
                std::cerr << "Error: No output filename provided. Use -h or --help for usage." << std::endl;
                return false;
            }
        }
        else if (strcmp(argv[i], "-i") == 0 || strcmp(argv[i], "--iterations") == 0)
        {
            if (i + 1 < argc)
            {
                try
                {
                    iterations = std::stoul(argv[++i]);
                }
                catch (const std::invalid_argument& e)
                {
                    std::cerr << "Error: Invalid value for iterations. Use -h or --help for usage." << std::endl;
                    return false;
                }
            }
            else
            {
                std::cerr << "Error: No value for iterations provided. Use -h or --help for usage." << std::endl;
                return false;
            }
        }
        else if (strcmp(argv[i], "-m") == 0 || strcmp(argv[i], "--mode") == 0)
        {
            if (i + 1 < argc)
            {
                std::string input_mode = std::string(argv[++i]);
                if (input_mode == "offline")
                    mode = true;
                else if (input_mode == "online")
                    mode = false;
                else
                {
                    std::cerr << "Error: Invalid mode. Use 'offline' or 'online'. Use -h or --help for usage." << std::endl;
                    return false;
                }
            }
            else
            {
                std::cerr << "Error: No mode specified. Use -h or --help for usage." << std::endl;
                return false;
            }
        }
        else if (strcmp(argv[i], "-h") == 0 || strcmp(argv[i], "--help") == 0)
        {
            get_help();
            help_requested_ = true;
            return false;
        }
        else
        {
            std::cerr << "Error: Unknown option entered. Use -h or --help for usage." << std::endl;
            return false;
        }
    }

    if (!mode && iterations == 0)
        iterations = 1;

    return true;
}


void ConsoleParser::get_help()
{
    std::cout << "Usage: <program executable file> [options]" << std::endl;
    std::cout << "The program provides next options calling by the flags:" << std::endl;
    std::cout << "-f\t--file\tFILENAME\tInput file with universe inside." << std::endl;
    std::cout << "-o\t--output\tFILENAME\tOutput file for saving universe." << std::endl;
    std::cout << "-i\t--iterations\tNUMBER\tNumber of iterations to run." << std::endl;
    std::cout << "-m\t--mode\tMODE\tMode of the game (online or offline)." << std::endl;
    std::cout << "-h\t--help\tDisplays this help menu and exit program." << std::endl;
}