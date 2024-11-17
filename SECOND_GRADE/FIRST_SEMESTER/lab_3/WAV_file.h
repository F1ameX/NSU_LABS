#pragma once

#include <algorithm>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
#include "exceptions.h"
#include "tick.h"


class WAVFile
{
public:
    WAVFile(const std::string& filepath);
    WAVFile(const std::string& filepath, const std::vector<tick>& samples, int sample_rate = 44100);

    bool read();
    bool write();

    const std::vector<tick>& get_samples() const;
    int get_sample_rate() const;

private:
    std::string filepath_;
    std::vector<tick> samples_;
    int sample_rate_;
    bool valid_format_;

    bool read_header(std::ifstream& file);
    bool write_header(std::ofstream& file);
};