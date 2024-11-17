#include "input_parser.h"

InputParser::InputParser(int argc, char* argv[]) : argc_(argc), argv_(argv), show_help_(false) {}

bool InputParser::show_help() const { return show_help_; }
const std::string& InputParser::get_config_file_path() const { return config_file_; }
const std::string& InputParser::get_output_file_path() const { return output_file_; }
const std::vector<std::string>& InputParser::get_input_files() const { return input_files_; }
const std::vector<std::unique_ptr<AudioConverter>>& InputParser::get_mute_commands() const { return mute_commands_; }
const std::vector<std::unique_ptr<AudioConverter>>& InputParser::get_mix_commands() const { return mix_commands_; }
const std::vector<std::unique_ptr<AudioConverter>>& InputParser::get_echo_commands() const { return echo_commands_; }


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

        try
        {
            return parse_config_file();
        }
        catch (const ConfigParseError& e)
        {
            std::cerr << "Configuration Error: " << e.what() << std::endl;
            return false;
        }
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
        throw FileReadError("Could not open the configuration file: " + config_file_);

    std::string line;
    while (std::getline(config, line))
    {
        if (line.empty() || line[0] == '#') continue;

        std::istringstream iss(line);
        Command cmd;
        iss >> cmd.type;
        std::string arg;

        while (iss >> arg)
            cmd.args.push_back(arg);

        process_command(cmd);
    }
    config.close();
    return true;
}


void InputParser::process_command(const Command& cmd)
{
    if (cmd.type == "mute" && cmd.args.size() == 2)
    {
        try
        {
            auto converter = AudioConverterFactory::createConverter("mute", {cmd.args[0], cmd.args[1]});
            if (converter)
            {
                mute_commands_.push_back(std::move(converter));
                std::cout << "Mute command added." << std::endl;
            }
            else
                throw InvalidCommandError("Failed to create mute converter.");
        }
        catch (const std::exception& e)
        {
            throw InvalidCommandError("Error: Invalid parameters for mute command: " + std::string(e.what()));
        }
    }
    else if (cmd.type == "mix" && cmd.args.size() == 2)
    {
        try
        {
            std::string additional_stream = cmd.args[0];
            int insert_position = std::stoi(cmd.args[1]);

            auto converter = AudioConverterFactory::createConverter("mix", {additional_stream, std::to_string(insert_position)});

            if (converter)
            {
                mix_commands_.push_back(std::move(converter));
                std::cout << "Mix command added." << std::endl;
            }
            else
                throw InvalidCommandError("Failed to create mix converter.");
        }
        catch (const std::exception& e)
        {
            throw InvalidCommandError("Error: Invalid parameters for mix command: " + std::string(e.what()));
        }
    }
    else if (cmd.type == "echo" && cmd.args.size() == 2)
    {
        try
        {
            auto converter = AudioConverterFactory::createConverter("echo", cmd.args);
            if (converter)
            {
                echo_commands_.push_back(std::move(converter));
                std::cout << "Echo command added." << std::endl;
            }
            else
                throw InvalidCommandError("Failed to create echo converter.");
        }
        catch (const std::exception& e)
        {
            throw InvalidCommandError("Error: Invalid parameters for echo command: " + std::string(e.what()));
        }
    }
    else
        throw UnknownCommandError("Unknown or malformed command in config: " + cmd.type);
}


std::string InputParser::get_help_message()
{
    std::ostringstream oss;
    oss << "Usage: sound_processor [-h] [-c config.txt output.wav input1.wav [input2.wav …]]\n";
    oss << "Options (flags):\n";
    oss << "  -h                  Show this help message and exit\n";
    oss << "  -c config.txt       Specify the configuration file, output file, and input WAV files\n\n";
    oss << AudioConverterFactory::get_supported_converters();
    return oss.str();
}