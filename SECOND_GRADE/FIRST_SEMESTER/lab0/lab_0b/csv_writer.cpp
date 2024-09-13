#include "csv_writer.h"

void CSVWriter::write_to_file(const std::string& output_file_name, const std::map<std::string, int>& words_map, int words_quantity)
{
    std::ofstream file_csv("/Users/andrewf1amex/Programming/lab_0b/" + output_file_name);

    if (!file_csv.is_open())
    {
        std::cerr << "Wrong path or name to the file. Please ensure in right output file name and retry!" << std::endl;
        return;
    }

    std::vector<std::tuple<std::string, int, float>> words_frequency;

    for (const auto& [word, count] : words_map)
    {
        float percent = (static_cast<float>(count) / static_cast<float>(words_quantity)) * 100;
        words_frequency.emplace_back(word, count, percent);
    }

    std::sort(words_frequency.begin(), words_frequency.end(), [](const auto& a, const auto& b) {return std::get<2>(a) < std::get<2>(b);});

    file_csv << "Слово,Частота,Частота(%)\n";
    for (const auto& [word, count, percent] : words_frequency)
        file_csv << word << ',' << count << ',' << percent << '\n';

    file_csv.close();
}
