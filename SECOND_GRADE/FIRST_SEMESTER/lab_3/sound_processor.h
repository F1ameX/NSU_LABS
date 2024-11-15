#pragma once

#include "exceptions.h"
#include "input_parser.h"
#include "WAV_file.h"
#include "audio_converters.h"
#include <vector>
#include <string>
#include <iostream>
#include <memory>

class SoundProcessor {
public:
    explicit SoundProcessor(const InputParser& parser);
    bool run();

private:
    const InputParser& parser_;
    void apply_mute_commands(std::vector<tick>& samples);
    bool apply_mix_commands(std::vector<tick>& samples);
    void apply_echo_commands(std::vector<tick>& samples);
};