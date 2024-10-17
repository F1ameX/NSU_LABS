#include "console_parser.h"

ConsoleParser::ConsoleParser() : iterations(0), mode(false), input_file("none"), output_file("none") {}

bool ConsoleParser::is_offline_mode() const { return mode; }
std::size_t ConsoleParser::get_iterations() const { return iterations; }
std::string ConsoleParser::get_input_file() const { return input_file; }
std::string ConsoleParser::get_output_file() const { return output_file; }

bool ConsoleParser::parse(int argc, char* argv[])
{
    for (size_t i = 1; i < argc; i++)
    {
        const char* current_arg = argv[i];

        if (strcmp(current_arg, "-f") == 0 || strcmp(current_arg, "--file") == 0)
        {
            if (i + 1 < argc)
                input_file = std::string(argv[++i]);
            else
            {
                std::cerr << "Error. Can't read input filename. For usage call -h or --help flag." << std::endl;
                return false;
            }
        }
        else if (strcmp(current_arg, "-o") == 0 || strcmp(current_arg, "--output") == 0)
        {
            if (i + 1 < argc)
                output_file = std::string(argv[++i]);
            else
            {
                std::cerr << "Error. Can't read output filename. For usage call -h or --help flag." << std::endl;
                return false;
            }
        }
        else if (strcmp(current_arg, "-i") == 0 || strcmp(current_arg, "--iterations") == 0)
        {
            if (i + 1 < argc)
            {
                try
                {
                    iterations = std::stoul(argv[++i]);
                }
                catch (const std::invalid_argument& e)
                {
                    std::cerr << "Error. Invalid value for iterations. For usage call -h or --help flag." << std::endl;
                    return false;
                }
            }
            else
            {
                std::cerr << "Error. Can't read iterations quantity. For usage call -h or --help flag." << std::endl;
                return false;
            }
        }
        else if (strcmp(current_arg, "-m") == 0 || strcmp(current_arg, "--mode") == 0)
        {
            if (i + 1 < argc)
            {
                std::string input_mode = std::string(argv[++i]);

                if (input_mode != "offline" && input_mode != "online")
                {
                    std::cerr << "Error. Wrong game mode entered. For usage call -h or --help flag." << std::endl;
                    return false;
                }
                mode = (input_mode == "offline");
            }
            else
            {
                std::cerr << "Error. Can't read game mode. For usage call -h or --help flag." << std::endl;
                return false;
            }
        }
        else if (strcmp(current_arg, "-h") == 0 || strcmp(current_arg, "--help") == 0)
        {
            get_help();
            exit(0);
        }

        else
        {
            std::cerr << "Error. Unknown option entered. For usage call -h or --help flag." << std::endl;
            return false;
        }
    }

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