#include "console_parser.h"
#include "file_manager.h"


int main(int argc, char* argv[])
{
    ConsoleParser parser;
    FileManager filestream;

    if (!parser.parse(argc, argv))
        return 0;
    else
    {

    }
}