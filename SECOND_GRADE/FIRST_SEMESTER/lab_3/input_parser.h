#include <string>
#include <vector>
#include <fstream>
#include <sstream>
#include <iostream>


struct Command
{
    std::string type;
    std::vector<std::string> args;
};

class InputParser {
public:
    InputParser(int argc, char* argv[]);

    bool parse();
    bool show_help() const;

    std::string get_config_file_path() const;
    std::string get_output_file_path() const;
    std::vector<std::string> get_input_files() const;
    std::vector<Command> get_commands() const;

    static std::string get_help_message();

private:
    int argc_;
    char** argv_;
    bool show_help_;

    std::string config_file_;
    std::string output_file_;
    std::vector<std::string> input_files_;
    std::vector<Command> commands_;

    bool parse_config_file();
};

