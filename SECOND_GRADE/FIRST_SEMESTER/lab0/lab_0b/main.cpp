#include <iostream>
#include <fstream>
#include <map>
#include <list>
#include <regex>

using namespace std;

class WordData {
private:
    int words_counter = 0;
    list<string> input_file_strings;
    map<string, int> words_map;

public:
    int get_words_counter() const { return words_counter; }
    const map<string, int>& get_words_map() const { return words_map; }

    void read_from_file(const string& input_file_name)
    {
        string file_string;
        ifstream file_txt("/Users/andrewf1amex/Programming/cpp_test/" + input_file_name);

        if (!file_txt.is_open())
            cerr << "Wrong path or name to the file. Please ensure in right output file name and retry!" << endl;

        while (getline(file_txt, file_string))
            input_file_strings.push_back(file_string);
        file_txt.close();
    }

    void get_data_from_file()
    {
        regex word_regex("[\\w]+");
        for (const auto& line : input_file_strings) {
            auto words_begin = sregex_iterator(line.begin(), line.end(), word_regex);
            auto words_end = sregex_iterator();
            for (auto i = words_begin; i != words_end; ++i) {
                string word = (*i).str();
                transform(word.begin(), word.end(), word.begin(), ::tolower);
                words_counter++;
                words_map[word]++;
            }
        }
    }

    void process_file(const string& input_file_name)
    {
        read_from_file(input_file_name);
        get_data_from_file();
    }
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