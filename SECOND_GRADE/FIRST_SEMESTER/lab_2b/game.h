#pragma once

#include <iostream>


class Game{
private:
    int current_iteration;
    int field_size;
    std::vector<std::vector<char>> game_field;
    std::string transition_rule;
public:
    Game();
    ~Game();

    void initialize_field();
    void display_field();
};