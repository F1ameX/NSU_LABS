#pragma once

#include "file_manager.h"
#include "console_parser.h"
#include <iostream>
#include <cstdlib>


class Game {
private:
    int field_size;
    int current_iteration;
    std::string universe_name;
    std::string rule;
    std::vector<std::vector<bool>> game_field;
public:
    Game(int field_size);
    ~Game();

    static bool is_valid_rule(const std::string& rule);
    bool prepare_game(ConsoleParser& parser, FileManager& file_manager);
    void generate_random_universe();
};
