#include <iostream>
#include "csv_writer.h"
#include "word_data.h"

using namespace std;


int main(int argc, char** argv)
{
    if (argc != 3)
    {
        cerr << "Usage: " << argv[0] << " input.txt output.csv" << endl;
        return 0;
    }

    string input_file_name = argv[1];
    string output_file_name = argv[2];

    WordData word_data;
    word_data.process_file(input_file_name);

    CSVWriter::write_to_file(output_file_name, word_data.get_words_map(), word_data.get_words_counter());

    return 0;
}