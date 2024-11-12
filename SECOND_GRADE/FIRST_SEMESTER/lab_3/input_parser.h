#pragma once

#include <string>
#include <vector>
#include <memory>
#include <fstream>
#include <iostream>
#include <sstream>

struct Command
{
    std::string type;
    std::vector<std::string> args;
};


struct MuteCommand
{
    int start_time;
    int end_time;
};

struct MixCommand
{
    std::string additional_stream;
    int insert_position;
};

struct EchoCommand
{
    int delay;
    float decay;
};

class InputParser
{
public:
    InputParser(int argc, char* argv[]);

    bool show_help() const;
    std::string get_config_file_path() const;
    std::string get_output_file_path() const;
    std::vector<std::string> get_input_files() const;

    bool parse();

    std::vector<MuteCommand> get_mute_commands() const;
    std::vector<MixCommand> get_mix_commands() const;
    std::vector<EchoCommand> get_echo_commands() const;

    static std::string get_help_message();

private:
    int argc_;
    char** argv_;
    bool show_help_;
    std::string config_file_;
    std::string output_file_;
    std::vector<std::string> input_files_;

    std::vector<MuteCommand> mute_commands_;
    std::vector<MixCommand> mix_commands_;
    std::vector<EchoCommand> echo_commands_;
    bool parse_config_file();
    void process_command(const Command& cmd);
};