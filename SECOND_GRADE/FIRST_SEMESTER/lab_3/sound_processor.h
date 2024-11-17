#pragma once

#include "exceptions.h"
#include "input_parser.h"
#include "WAV_file.h"
#include "audio_converters.h"
#include <vector>
#include <string>
#include <iostream>
#include <memory>

class SoundProcessor
{
public:
    explicit SoundProcessor(const InputParser& parser);
    bool run();

private:
    const InputParser& parser_;
    bool apply_commands(std::vector<tick>& samples);
};