#include "input_parser.h"
#include "sound_processor.h"
#include <iostream>


int main(int argc, char* argv[])
{
    InputParser parser(argc, argv);

    if (!parser.parse())
        return 1;

    if (parser.show_help())
    {
        std::cout << InputParser::get_help_message() << std::endl;
        return 0;
    }

    SoundProcessor processor(parser);
    if (!processor.run())
    {
        std::cerr << "Error: Processing failed." << std::endl;
        return 1;
    }

    return 0;
}