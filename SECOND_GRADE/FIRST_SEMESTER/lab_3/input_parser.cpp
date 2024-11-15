#include "input_parser.h"

InputParser::InputParser(int argc, char* argv[]) : argc_(argc), argv_(argv), show_help_(false) {}

bool InputParser::show_help() const { return show_help_; }
const std::string& InputParser::get_config_file_path() const { return config_file_; }
const std::string& InputParser::get_output_file_path() const { return output_file_; }
const std::vector<std::string>& InputParser::get_input_files() const { return input_files_; }
const std::vector<MuteCommand>& InputParser::get_mute_commands() const { return mute_commands_; }
const std::vector<MixCommand>& InputParser::get_mix_commands() const { return mix_commands_; }
const std::vector<EchoCommand>& InputParser::get_echo_commands() const { return echo_commands_; }

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
        int start_time = std::stoi(cmd.args[0]);
        int end_time = std::stoi(cmd.args[1]);

        if (start_time >= 0 && end_time > start_time)
        {
            MuteCommand mute_cmd = {start_time, end_time};
            mute_commands_.push_back(mute_cmd);
        }
        else
            throw InvalidCommandError("Invalid parameters for mute command: " + std::to_string(start_time) + " " + std::to_string(end_time));
    }
    else if (cmd.type == "mix" && cmd.args.size() == 2)
    {
        try
        {
            int insert_position = std::stoi(cmd.args[1]);
            MixCommand mix_cmd = {cmd.args[0], insert_position};
            mix_commands_.push_back(mix_cmd);
        }
        catch (const std::exception& e)
        {
            throw InvalidCommandError("Invalid parameters for mix command: " + cmd.args[0] + " " + cmd.args[1]);
        }
    }
    else if (cmd.type == "echo" && cmd.args.size() == 2)
    {
        try
        {
            int delay = std::stoi(cmd.args[0]);
            float decay = std::stof(cmd.args[1]);

            if (delay >= 0 && decay >= 0.0f && decay <= 1.0f)
            {
                EchoCommand echo_cmd = {delay, decay};
                echo_commands_.push_back(echo_cmd);
            }
            else
                throw InvalidCommandError("Invalid parameters for echo command: " + std::to_string(delay) + " " + std::to_string(decay));
        }
        catch (const std::exception& e)
        {
            throw InvalidCommandError("Invalid parameters for echo command: " + cmd.args[0] + " " + cmd.args[1]);
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