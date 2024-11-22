#pragma once

#include <algorithm>
#include <vector>
#include <string>
#include <memory>
#include <iostream>
#include "tick.h"
#include "WAV_file.h"

static constexpr int sample_rate = 44100;

class AudioConverter
{
public:
    virtual void apply(std::vector<tick>& samples) = 0;
    virtual ~AudioConverter() = default;
};


class MuteConverter : public AudioConverter
{
public:
    MuteConverter(int start_time, int end_time);
    void apply(std::vector<tick>& samples) override;
private:
    size_t start_time_;
    size_t end_time_;
};


class MixConverter : public AudioConverter
{
public:
    MixConverter(const std::string& additional_stream, int insert_position);
    void apply(std::vector<tick>& samples) override;
private:
    int insert_position_;
    std::string additional_stream_;
    std::vector<tick> mix_samples_;
};


class EchoConverter : public AudioConverter
{
public:
    EchoConverter(size_t delay, float decay);
    void apply(std::vector<tick>& samples) override;
private:
    size_t delay_;
    float decay_;
};


class AudioConverterFactory
{
public:
    template <typename ConverterType>
    static std::unique_ptr<AudioConverter> create_converter(const std::vector<std::string>& args);
};


template <>
std::unique_ptr<AudioConverter> AudioConverterFactory::create_converter<MuteConverter>(const std::vector<std::string>& args);

template <>
std::unique_ptr<AudioConverter> AudioConverterFactory::create_converter<MixConverter>(const std::vector<std::string>& args);

template <>
std::unique_ptr<AudioConverter> AudioConverterFactory::create_converter<EchoConverter>(const std::vector<std::string>& args);