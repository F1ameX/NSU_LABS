#pragma once

#include "tick.h"
#include <vector>
#include <memory>
#include <string>

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
    void apply(std::vector<tick>& samples) override;
    MuteConverter(int start, int end);

};


class MixConverter : public AudioConverter
{
private:
    std::vector<tick> mix_samples_;
    int insert_position_;

public:
    void apply(std::vector<tick>& samples) override;
    MixConverter(const std::vector<tick>& mix_samples, int insert_position);

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
    static std::unique_ptr<AudioConverter> createConverter(const std::string& type, const std::vector<std::string>& args);
};