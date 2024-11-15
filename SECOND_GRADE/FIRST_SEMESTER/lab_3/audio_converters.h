#pragma once

#include <algorithm>
#include <cstdlib>
#include <iostream>
#include <memory>
#include <sstream>
#include <string>
#include <vector>
#include "tick.h"

class AudioConverter
{
public:
    virtual ~AudioConverter() = default;
    virtual void apply(std::vector<tick>& samples) = 0;
};


class MuteConverter : public AudioConverter
{
private:
    int start_time_;
    int end_time_;

public:
    MuteConverter(int start, int end);
    void apply(std::vector<tick>& samples) override;
};


class MixConverter : public AudioConverter
{
private:
    std::vector<tick> mix_samples_;
    int insert_position_;

public:
    MixConverter(const std::vector<tick>& mix_samples, int insert_position);
    void apply(std::vector<tick>& samples) override;
};


class EchoConverter : public AudioConverter
{
private:
    int delay_;
    float decay_;

public:
    EchoConverter(int delay, float decay);
    void apply(std::vector<tick>& samples) override;
};


class AudioConverterFactory
{
public:
    static std::unique_ptr<AudioConverter> createConverter(const std::string &type, const std::vector<std::string> &args);
    static std::string get_supported_converters();
};