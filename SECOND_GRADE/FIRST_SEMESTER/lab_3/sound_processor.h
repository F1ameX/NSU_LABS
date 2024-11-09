#pragma once

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
};
