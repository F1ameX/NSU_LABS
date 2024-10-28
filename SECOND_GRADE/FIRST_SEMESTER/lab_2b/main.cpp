#include "console_parser.h"
#include "file_manager.h"
#include "game.h"
#include <iostream>

int main(int argc, char* argv[])
{
    ConsoleParser parser;
    if (!parser.parse(argc, argv)) {
        std::cerr << "Error: Failed to parse command line arguments." << std::endl;
        return 1;
    }

    int field_size = 20;
    Game game(field_size);
    FileManager file_manager;

    if (!game.prepare_game(parser, file_manager))
    {
        std::cerr << "Error: Failed to prepare game." << std::endl;
        return 1;
    }

    if (parser.is_offline_mode())
    {
        game.run_iterations(parser.get_iterations());

        FileManager::save_to_file(parser.get_output_file(), game.get_field(), game.get_universe_name(), game.get_rule());
        std::cout << "Offline mode completed: output saved to " << parser.get_output_file() << std::endl;
    }

    else
        game.run();

    return 0;
}
