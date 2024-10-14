#include "game.h"

Game::Game() : current_iteration(0), game_field(field_size, std::vector<char>(field_size)) {initialize_field();}
Game::~Game() = default;

void Game::initialize_field()
{
for (int i = 0; i < field_size; i++)
for (int j = 0; j < field_size; j++)
game_field[i][j] = '0';
}


void Game::display_field()
{
    for (int i = 0; i < field_size; i++)
    {
        for (int j = 0; j < field_size; j++)
            std::cout << game_field[i][j] << ' ';
        std:: cout << std::endl;
    }
}

