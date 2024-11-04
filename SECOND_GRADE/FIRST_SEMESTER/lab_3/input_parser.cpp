#include "input_parser.h"

InputParser::InputParser(int argc, char* argv[]) : argc_(argc), argv_(argv), show_help_(false) {}

bool InputParser::show_help() const { return show_help_; }

std::string InputParser::get_config_file_path() const { return config_file_; }
std::string InputParser::get_output_file_path() const { return output_file_; }
std::vector<std::string> InputParser::get_input_files() const { return input_files_; }
std::vector<Command> InputParser::get_commands() const { return commands_;}


bool InputParser::parse()
{
    if (argc_ < 2)
    {
        std::cerr << "Error! Not enough arguments entered. Use -h flag for help." << std::endl;
        return false;
    }


    int argv_index = 1;
    std::string arg = argv_[argv_index];

    if (arg == "-h")
    {
        show_help_ = true;
        return true;
    }

    else if (arg == "-c")
    {
        if (argv_index + 3 >= argc_)
        {
            std::cerr << "Error! Bad arguments for -c flag. Use -h flag for help." << std::endl;
            return false;
        }

        config_file_ = argv_[++argv_index];
        output_file_ = argv_[++argv_index];

        for (++argv_index; argv_index < argc_; ++argv_index)
            input_files_.emplace_back(argv_[argv_index]);

        if (input_files_.empty())
        {
            std::cerr << "Error! No input files specified. Use -h flag for help." << std::endl;
            return false;
        }

        return parse_config_file();
    }

    else
    {
        std::cerr << "Error! Unknown argument: " << arg << std::endl;
        return false;
    }
}


bool InputParser::parse_config_file()
{
    std::ifstream config(config_file_);
    if (!config.is_open())
    {
        std::cerr << "Error! Could`t open the configuration file: " << config_file_ << "\n";
        return false;
    }

    std::string line;
    while (std::getline(config, line))
    {

        if (line.empty() || line[0] == '#') continue;

        std::istringstream iss(line);
        std::string command_type;
        iss >> command_type;

        Command cmd;
        cmd.type = command_type;

        std::string arg;
        while (iss >> arg)
            cmd.args.push_back(arg);

        commands_.push_back(cmd);
    }

    config.close();
    return true;
}


std::string InputParser::get_help_message()
{
    return "Usage: sound_processor [-h] [-c config.txt output.wav input1.wav [input2.wav …]]\n"
           "Options (flags):\n"
           "  -h                  Show this help message and exit from the programm\n"
           "  -c config.txt       Specify the configuration file, output file and input WAV files\n";
}