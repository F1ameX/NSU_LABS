#include "input_parser.h"
#include "sound_processor.h"
#include <iostream>


int main(int argc, char* argv[])
{
    InputParser parser(argc, argv);
    if (!parser.parse())
    {
        std::cerr << parser.get_help_message() << std::endl;
        return 1;
    }

    SoundProcessor processor(parser);
    if (!processor.run())
    {
        std::cerr << "Processing failed." << std::endl;
        return 1;
    }

    return 0;
}
