#include "game.h"
#include <sstream>

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


int Game::count_alive_neighbors(int x, int y) const
{
    int alive_neighbors = 0;
    for (int dx = -1; dx <= 1; ++dx)
    {
        for (int dy = -1; dy <= 1; ++dy)
        {
            if (dx == 0 && dy == 0) continue;
            int nx = (x + dx + field_size) % field_size;
            int ny = (y + dy + field_size) % field_size;
            if (game_field[nx][ny].is_alive()) ++alive_neighbors;
        }
    }
    return alive_neighbors;
}

void Game::run_iteration()
{
    for (int x = 0; x < field_size; ++x)
    {
        for (int y = 0; y < field_size; ++y)
        {
            int alive_neighbors = count_alive_neighbors(x, y);
            bool next_state = false;

            if (game_field[x][y].is_alive())
            {
                next_state = (rule.find('S' + std::to_string(alive_neighbors)) != std::string::npos);
            }
            else
            {
                next_state = (rule.find('B' + std::to_string(alive_neighbors)) != std::string::npos);
            }

            game_field[x][y].set_next_state(next_state);
        }
    }

    for (int x = 0; x < field_size; ++x)
    {
        for (int y = 0; y < field_size; ++y)
        {
            game_field[x][y].apply_next_state();
        }
    }

    ++current_iteration;
}

void Game::display() const
{
    std::cout << "Universe: " << universe_name << ", Rule: " << rule << ", Iteration: " << current_iteration << std::endl;
    for (int x = 0; x < field_size; ++x)
    {
        for (int y = 0; y < field_size; ++y)
        {
            std::cout << (game_field[x][y].is_alive() ? 'O' : '.');
        }
        std::cout << '\n';
    }
}

void Game::save_to_file(const std::string& filename)
{
    FileManager::save_to_file(filename, game_field, universe_name, rule);
    std::cout << "Universe saved to " << filename << std::endl;
}

void Game::run()
{
    std::string command;
    while (true)
    {
        std::cout << "Enter command (tick, dump, exit, help): ";
        std::getline(std::cin, command);
        if (!execute_command(command))
        {
            break;
        }
    }
}

bool Game::execute_command(const std::string& command)
{
    std::istringstream iss(command);
    std::string cmd;
    iss >> cmd;

    if (cmd == "tick" || cmd == "t")
    {
        int iterations = 1;
        if (iss >> iterations)
        {
            run_iterations(iterations);
        }
        else
        {
            run_iterations(1);
        }
        display();
    }
    else if (cmd == "dump")
    {
        std::string filename;
        if (iss >> filename)
        {
            save_to_file(filename);
        }
        else
        {
            std::cerr << "Error: No filename provided for dump command." << std::endl;
        }
    }
    else if (cmd == "exit")
    {
        return false;
    }
    else if (cmd == "help")
    {
        std::cout << "Available commands:\n"
                  << "  tick <n=1> - Perform n iterations (default is 1)\n"
                  << "  dump <filename> - Save the current state to a file\n"
                  << "  exit - End the game\n"
                  << "  help - Show this help message\n";
    }
    else
    {
        std::cerr << "Error: Unknown command." << std::endl;
    }

    return true;
}

void Game::run_iterations(int n)
{
    for (int i = 0; i < n; ++i)
    {
        run_iteration();
    }
}
