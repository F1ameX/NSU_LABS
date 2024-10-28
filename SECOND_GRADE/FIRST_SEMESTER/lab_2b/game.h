#pragma once

#include "console_parser.h"
#include "file_manager.h"
#include "cell.h"
#include <vector>
#include <iostream>

class Game {
private:
    int field_size;
    int current_iteration;
    std::vector<std::vector<Cell>> game_field;
    std::string universe_name;
    std::string rule;

public:
    Game(int field_size);
    ~Game();

    bool prepare_game(ConsoleParser& parser, FileManager& file_manager);
    void run();
    void run_iterations(int n);

    void display() const;
    const std::vector<std::vector<Cell>>& get_field() const { return game_field; }
    const std::string& get_universe_name() const { return universe_name; }
    const std::string& get_rule() const { return rule; }
private:
    void generate_random_universe();
    bool is_valid_rule(const std::string& rule);
    int count_alive_neighbors(int x, int y) const;
    void run_iteration();
    bool execute_command(const std::string& command);
    void save_to_file(const std::string& filename);
};