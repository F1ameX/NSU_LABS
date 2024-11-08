#include "audio_converters.h"
#include <algorithm>
#include <cstdlib>


MuteConverter::MuteConverter(int start, int end) : start_time_(start), end_time_(end) {}
MixConverter::MixConverter(const std::vector<tick>& mix_samples, int insert_position)
        : mix_samples_(mix_samples), insert_position_(insert_position) {}
EchoConverter::EchoConverter(int delay, float decay) : delay_(delay), decay_(decay) {}


void MuteConverter::apply(std::vector<tick>& samples)
{
    for (size_t i = start_time_; i < end_time_ && i < samples.size(); ++i)
        samples[i] = 0;
}


void MixConverter::apply(std::vector<tick>& samples)
{
    for (size_t i = 0; i < mix_samples_.size() && (i + insert_position_) < samples.size(); ++i)
        samples[i + insert_position_] = std::clamp(samples[i + insert_position_] + mix_samples_[i], -32768, 32767);
}


void EchoConverter::apply(std::vector<tick>& samples)
{
    for (size_t i = delay_; i < samples.size(); ++i)
        samples[i] = std::clamp(static_cast<int>(samples[i] + samples[i - delay_] * decay_), -32768, 32767);
}


std::unique_ptr<AudioConverter> AudioConverterFactory::createConverter(const std::string& type, const std::vector<std::string>& args)
{
    if (type == "mute" && args.size() == 2)
    {
        int start = std::stoi(args[0]);
        int end = std::stoi(args[1]);
        return std::make_unique<MuteConverter>(start, end);
    }

    else if (type == "mix" && args.size() >= 2)
    {
        int insert_position = std::stoi(args[0]);
        std::vector<tick> mix_samples(args.size() - 1);

        for (size_t i = 1; i < args.size(); ++i)
            mix_samples[i - 1] = static_cast<tick>(std::stoi(args[i]));

        return std::make_unique<MixConverter>(mix_samples, insert_position);
    }

    else if (type == "echo" && args.size() == 2) {
        int delay = std::stoi(args[0]);
        float decay = std::stof(args[1]);
        return std::make_unique<EchoConverter>(delay, decay);
    }

    return nullptr;
}