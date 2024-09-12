#include "csv_writer.h"

void CSVWriter::write_to_file(const std::string& output_file_name, const std::map<std::string, int>& words_map, int words_quantity) {
    std::ofstream file_csv(output_file_name);

    if (!file_csv.is_open())
        std::cerr << "Wrong path or name to the file. Please ensure in right output file name and retry!" << std::endl;

    file_csv << "Слово,Частота,Частота(%)\n";
    for (const auto& [word, count] : words_map)
        file_csv << word << ',' << count << ',' << (float(count) / float(words_quantity)) * 100 << '\n';

    file_csv.close();
}