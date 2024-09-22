#include "word_data.h"

int WordData::get_words_counter() const { return words_counter; }
const std::map<std::string, int>& WordData::get_words_map() const { return words_map; }

void WordData::process_file_data(const std::string& input_file_name)
{
    std::string file_string;
    std::ifstream file_txt("/Users/andrewf1amex/Programming/lab_0b/" + input_file_name);

    if (!file_txt.is_open())
        std::cerr << "Wrong path or name to the file. Please ensure in right output file name and retry!" << std::endl;

    std::regex word_regex("[\\w]+");
    while (getline(file_txt, file_string))
    {
        auto words_begin = std::sregex_iterator(file_string.begin(), file_string.end(), word_regex);
        auto words_end = std::sregex_iterator();
        for (auto i = words_begin; i != words_end; ++i)
        {
            std::string word = (*i).str();
            std::transform(word.begin(), word.end(), word.begin(), ::tolower);
            words_counter++;
            words_map[word]++;
        }
    }

    file_txt.close();
}