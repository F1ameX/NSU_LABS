#pragma once
#include "cell.h"
#include "console_parser.h"
#include <fstream>
#include <iostream>
#include <vector>
#include <sstream>


class Game {
private:
    int field_size;
    int current_iteration;

    std::vector<std::vector<Cell>> game_field;
    std::string universe_name;
    std::string rule;

    friend std::ostream& operator<<(std::ostream& os, const Game& game);
    friend std::istream& operator>>(std::istream& is, Game& game);

public:
    explicit Game(int field_size);
    ~Game();

    bool prepare_game(const ConsoleParser& parser);
    bool is_valid_rule(const std::string& rule);
    bool execute_command(const std::string& command);

    void run();
    void run_iterations(int n);
    void display() const;
    void generate_random_universe();
    void run_iteration();

    [[nodiscard]] int count_alive_neighbors(int x, int y) const;
    [[nodiscard]] std::vector<std::vector<Cell>>& get_field();
    [[nodiscard]] const std::string& get_universe_name() const;
    [[nodiscard]] const std::string& get_rule() const;
};