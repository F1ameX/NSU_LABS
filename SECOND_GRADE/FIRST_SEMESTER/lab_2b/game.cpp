#include "game.h"


Game::Game(int field_size) : field_size(field_size), current_iteration(0), game_field(field_size, std::vector<Cell>(field_size)) {}
Game::~Game() = default;


void Game::generate_random_universe()
{
    for (std::size_t x = 0; x < field_size; x++)
        for (std::size_t y = 0; y < field_size; y++)
            game_field[x][y].set_current_state(rand() % 2 == 0);
}


bool Game::is_valid_rule(const std::string& rule)
{
    if (rule[0] != 'B' || rule.find('/') == std::string::npos || rule[rule.find('/') + 1] != 'S')
        return false;

    if (!std::ranges::all_of(rule.substr(1, rule.find('/')), [](char c) { return c >= '0' && c <= '8'; }))
        return false;

    if (!std::ranges::all_of(rule.substr(rule.find('/') + 2), [](char c) { return c >= '0' && c <= '8'; }))
        return false;

    return true;
}


bool Game::prepare_game(ConsoleParser& parser, FileManager& file_manager)
{
    if (parser.is_offline_mode())
    {
        if (parser.get_input_file() == "none")
        {
            std::cout << "Warning: No input file provided. Generating random universe." << std::endl;
            generate_random_universe();
        }
        else
        {
            if (!file_manager.load_from_file(parser.get_input_file(), game_field, universe_name, rule))
            {
                std::cerr << "Error: Failed to load universe from input file." << std::endl;
                return false;
            }

            if (universe_name.empty())
            {
                std::cerr << "Warning: No universe name provided in the file. Using default name 'Unnamed'." << std::endl;
                universe_name = "Unnamed";
            }

            if (rule.empty() || !is_valid_rule(rule))
            {
                std::cerr << "Warning: No valid rule provided in the file. Using default rule 'B3/S23'." << std::endl;
                rule = "B3/S23";
            }
        }

        if (parser.get_output_file() == "none")
        {
            std::cerr << "Error: No output file specified in offline mode." << std::endl;
            return false;
        }
    }

    else
    {
        if (parser.get_input_file() == "none")
        {
            std::cerr << "Warning: No input file provided. Generating random universe in interactive mode." << std::endl;
            generate_random_universe();
        }

        else if (!file_manager.load_from_file(parser.get_input_file(), game_field, universe_name, rule))
        {
            std::cerr << "Error: Failed to load the universe from file in interactive mode." << std::endl;
            return false;
        }
    }

    if (parser.get_iterations() <= 0)
    {
        std::cerr << "Error: Number of iterations must be greater than zero." << std::endl;
        return false;
    }

    std::cout << "Loaded universe: " << universe_name << std::endl;
    std::cout << "Rule: " << rule << std::endl;
    std::cout << "Game prepared successfully!" << std::endl;

    return true;
}