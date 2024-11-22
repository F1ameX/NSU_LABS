#pragma once

#include <iostream>
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
    const InputParser& parser_;
};