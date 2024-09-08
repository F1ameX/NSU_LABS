#include <iostream>
#include <fstream>
#include <map>
#include <list>
#include <sstream>

using namespace std;


class WordData {
private:
    int words_counter = 0;
    list<string> input_file_strings;
    map<string, int> words_map;

public:
    static void read_from_file(const string& input_file_name, list<string>& input_file_strings)
    {
        string file_string;
        ifstream file_txt("/Users/andrewf1amex/Programming/cpp_test/" + input_file_name);

        if (!file_txt.is_open())
            cerr << "Wrong path or name to the file. Please ensure in right output file name and retry!" << endl;

        while (getline(file_txt, file_string))
            input_file_strings.push_back(file_string);
        file_txt.close();
    }

    static void get_data_from_file(const list<string>& input_file_strings, int& words_counter, map<string, int>& words_map)
    {
        string file_word;
        for (const auto& line : input_file_strings)
        {
            istringstream line_stream(line);
            while (line_stream >> file_word)
            {
                words_counter++;
                words_map[file_word]++;
            }
        }
    }

    void process_file(const string& input_file_name)
    {
        read_from_file(input_file_name, input_file_strings);
        get_data_from_file(input_file_strings, words_counter, words_map);
    }

    int get_words_counter() const { return words_counter; }
    const map<string, int>& get_words_map() const { return words_map; }
};


class CSVWriter {
public:
    static void write_to_file(const string& output_file_name, const map<string, int>& words_map, int words_quantity)
    {
        ofstream file_csv("/Users/andrewf1amex/Programming/cpp_test/" + output_file_name);

        if (!file_csv.is_open())
            cerr << "Wrong path or name to the file. Please ensure in right output file name and retry!" << endl;

        file_csv << "Слово,Частота,Частота(%)\n";
        for (const auto& [word, count] : words_map)
            file_csv << word << ',' << count << ',' << (float(count) / float(words_quantity)) * 100 << '\n';

        file_csv.close();
    }
};


int main(int argc, char** argv)
{
    int words_counter = 0;
    list<string> input_file_strings;
    map<string, int> words;
    WordData word_data;
    CSVWriter csv_writer;
    string input_file_name, output_file_name;

    if (argc != 3)
    {
        cerr << "Usage: " << argv[0] << " input.txt output.csv" << endl;
        return 0;
    }

    input_file_name = argv[1];
    output_file_name = argv[2];

    word_data.process_file(input_file_name);
    csv_writer.write_to_file(output_file_name, word_data.get_words_map(), word_data.get_words_counter());

    return 0;
}