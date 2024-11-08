#include "game.h"
#include <iostream>
#include <fstream>


int main(int argc, char* argv[])
{
    ConsoleParser parser;
    if (!parser.parse(argc, argv))
    {
        if (parser.help_requested())
            return 0;
        else
        {
            std::cerr << "Error: Failed to parse command line arguments." << std::endl;
            return 0;
        }
    }

    Game game(20);

    if (!game.prepare_game(parser))
    {
        std::cerr << "Error: Failed to prepare game." << std::endl;
        return 1;
    }

    if (parser.is_offline_mode())
    {
        game.run_iterations(parser.get_iterations());
        std::ofstream out_file(parser.get_output_file());

        if (out_file.is_open())
        {
            out_file << game;
            std::cout << "Offline mode completed: output saved to " << parser.get_output_file() << std::endl;
        }
        else
        {
            std::cerr << "Error: Could not open file " << parser.get_output_file() << std::endl;
            return 1;
        }
    }
    else
        game.run();

    return 0;
}