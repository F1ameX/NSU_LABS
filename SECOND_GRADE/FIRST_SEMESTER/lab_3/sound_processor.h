#pragma once

#include <vector>
#include <memory>
#include "input_parser.h"
#include "WAV_file.h"
#include "tick.h"

class SoundProcessor
{
public:
    SoundProcessor(const InputParser& parser);
    bool run();

private:
    void apply_mute_commands(std::vector<tick>& samples);
    void apply_mix_commands(std::vector<tick>& samples);
    void apply_echo_commands(std::vector<tick>& samples);

    const InputParser& parser_;
};