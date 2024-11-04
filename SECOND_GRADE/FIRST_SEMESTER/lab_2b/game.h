#pragma once
#include "cell.h"
#include "console_parser.h"
#include <fstream>
#include <iostream>
#include <vector>


class Game {
private:
    [[maybe_unused]] int field_size;
    int current_iteration;
    std::vector<std::vector<Cell>> game_field;
    std::string universe_name;
    std::string rule;
    friend std::ostream& operator<<(std::ostream& os, const Game& game);
    friend std::istream& operator>>(std::istream& is, Game& game);

public:
    Game(int field_size);
    ~Game();
    bool prepare_game(const ConsoleParser& parser);
    void run();
    void run_iterations(int n);
    void display() const;
    [[nodiscard]] const std::vector<std::vector<Cell>>& get_field() const { return game_field; }
    [[nodiscard]] const std::string& get_universe_name() const { return universe_name; }
    [[nodiscard]] const std::string& get_rule() const { return rule; }

private:
    void generate_random_universe();
    bool is_valid_rule(const std::string& rule);
    [[nodiscard]] int count_alive_neighbors(int x, int y) const;
    void run_iteration();
    bool execute_command(const std::string& command);
    void save_to_file(const std::string& filename);
};