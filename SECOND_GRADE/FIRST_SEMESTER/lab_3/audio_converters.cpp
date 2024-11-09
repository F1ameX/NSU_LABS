#include "audio_converters.h"


MuteConverter::MuteConverter(int start, int end)
        : start_time_(start * 44100 / 1000), end_time_(end * 44100 / 1000) {}
MixConverter::MixConverter(const std::vector<tick>& mix_samples, int insert_position)
        : mix_samples_(mix_samples), insert_position_(insert_position * 44100 / 1000) {}
EchoConverter::EchoConverter(int delay, float decay)
        : delay_(delay * 44100 / 1000), decay_(decay) {}


void MuteConverter::apply(std::vector<tick>& samples)
{
    std::cout << "Applying mute from sample " << start_time_ << " to sample " << end_time_ << std::endl;

    for (size_t i = start_time_; i < end_time_ && i < samples.size(); ++i)
        samples[i] = 0;

    std::cout << "Mute applied successfully" << std::endl;
}


void MixConverter::apply(std::vector<tick>& samples)
{
    std::cout << "Applying mix at sample position " << insert_position_ << std::endl;

    for (size_t i = 0; i < mix_samples_.size() && (i + insert_position_) < samples.size(); ++i)
        samples[i + insert_position_] = std::clamp(samples[i + insert_position_] + mix_samples_[i], -32768, 32767);

    std::cout << "Mix applied successfully" << std::endl;
}


void EchoConverter::apply(std::vector<tick>& samples)
{
    std::cout << "Applying echo with delay " << delay_ << " samples and decay " << decay_ << std::endl;

    for (size_t i = delay_; i < samples.size(); ++i)
    {
        int repeated_sample = samples[i - delay_];
        float decay_factor = decay_;

        for (int repeat = 1; repeat <= 5; ++repeat)
        {
            size_t echo_position = i + repeat * delay_;
            if (echo_position >= samples.size()) break;
            samples[echo_position] = std::clamp(static_cast<int>(samples[echo_position] + repeated_sample * decay_factor), -32768, 32767);
            decay_factor *= decay_;
        }
    }

    std::cout << "Echo applied successfully" << std::endl;
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

    else if (type == "echo" && args.size() == 2)
    {
        int delay = std::stoi(args[0]);
        float decay = std::stof(args[1]);
        return std::make_unique<EchoConverter>(delay, decay);
    }

    return nullptr;
}