#include "console_parser.h"
#include "file_manager.h"
#include "game.h"


int main(int argc, char* argv[])
{
    ConsoleParser parser;
    FileManager filestream;
    Game game(20);

    if (!parser.parse(argc, argv))
    {
        std::cerr << "Error: Failed to parse command line arguments." << std::endl;
        return 0;
    }

    if (!game.prepare_game(parser, filestream))
    {
        std::cerr << "Error: Failed to prepare game." << std::endl;
        return 0;
    }

    std::cout << "Game prepared and ready to start!" << std::endl;
    return 0;
}