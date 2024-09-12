#include "word_data.h"


int WordData::get_words_counter() const { return words_counter; }

const std::map<std::string, int>& WordData::get_words_map() const { return words_map; }

void WordData::read_from_file(const std::string& input_file_name)
{
    std::string file_string;
    std::ifstream file_txt(input_file_name);

    if (!file_txt.is_open())
        std::cerr << "Wrong path or name to the file. Please ensure in right output file name and retry!" << std::endl;

    while (getline(file_txt, file_string))
        input_file_strings.push_back(file_string);
    file_txt.close();
}

void WordData::get_data_from_file()
{
    std::regex word_regex("[\\w]+");
    for (const auto& line : input_file_strings)
    {
        auto words_begin = std::sregex_iterator(line.begin(), line.end(), word_regex);
        auto words_end = std::sregex_iterator();
        for (auto i = words_begin; i != words_end; ++i)
        {
            std::string word = (*i).str();
            std::transform(word.begin(), word.end(), word.begin(), ::tolower);
            words_counter++;
            words_map[word]++;
        }
    }
}

void WordData::process_file(const std::string& input_file_name)
{
    read_from_file(input_file_name);
    get_data_from_file();
}