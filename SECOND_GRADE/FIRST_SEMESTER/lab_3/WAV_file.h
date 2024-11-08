#include "tick.h"
#include <string>
#include <vector>
#include <fstream>
#include <iostream>
#include <stdexcept>


class WAVFile
{
public:
    WAVFile(const std::string& filepath);
    WAVFile(const std::string& filepath, const std::vector<tick>& samples, int sample_rate = 44100);

    bool read();
    bool write();

    const std::vector<tick>& get_samples() const;
    int get_sample_rate() const;
    bool is_valid_format() const;

private:
    std::string filepath_;
    std::vector<tick> samples_;
    int sample_rate_;
    bool valid_format_;

    bool read_header(std::ifstream& file);
    bool write_header(std::ofstream& file);
};
