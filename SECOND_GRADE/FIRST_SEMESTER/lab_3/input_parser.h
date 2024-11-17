#pragma once

#include <fstream>
#include <iostream>
#include <memory>
#include <sstream>
#include <string>
#include <vector>
#include "audio_converters.h"
#include "exceptions.h"

struct Command
{
    std::string type;
    std::vector<std::string> args;
};

class InputParser
{
public:
    InputParser(int argc, char* argv[]);

    bool show_help() const;
    const std::string& get_config_file_path() const;
    const std::string& get_output_file_path() const;
    const std::vector<std::string>& get_input_files() const;

    bool parse();

    const std::vector<std::unique_ptr<AudioConverter>>& get_mute_commands() const;
    const std::vector<std::unique_ptr<AudioConverter>>& get_mix_commands() const;
    const std::vector<std::unique_ptr<AudioConverter>>& get_echo_commands() const;

    static std::string get_help_message();

private:
    int argc_;
    char** argv_;
    bool show_help_;
    std::string config_file_;
    std::string output_file_;
    std::vector<std::string> input_files_;

    std::vector<std::unique_ptr<AudioConverter>> mute_commands_;
    std::vector<std::unique_ptr<AudioConverter>> mix_commands_;
    std::vector<std::unique_ptr<AudioConverter>> echo_commands_;

    bool parse_config_file();
    void process_command(const Command& cmd);
};