#include "audio_converters.h"

std::string AudioConverterFactory::get_supported_converters()
{
    std::ostringstream oss;
    oss << "Supported converters:\n";
    oss << "  mute <start> <end> - Mutes audio from start to end time (in ms).\n";
    oss << "      Parameters:\n";
    oss << "        start - Start time in milliseconds.\n";
    oss << "        end   - End time in milliseconds.\n\n";

    oss << "  mix <insert_position> <samples...> - Mixes additional samples at the specified position.\n";
    oss << "      Parameters:\n";
    oss << "        insert_position - Position in milliseconds where mixing starts.\n";
    oss << "        samples         - Additional samples to mix at insert_position.\n\n";

    oss << "  echo <delay> <decay> - Adds echo effect with specified delay and decay.\n";
    oss << "      Parameters:\n";
    oss << "        delay - Delay in milliseconds between echoes.\n";
    oss << "        decay - Decay factor (0.0 to 1.0), representing the decrease in volume for each echo.\n";

    return oss.str();
}


MuteConverter::MuteConverter(int start, int end) : start_time_(start * 44100 / 1000), end_time_(end * 44100 / 1000) {}
EchoConverter::EchoConverter(int delay, float decay): delay_(delay * 44100 / 1000), decay_(decay) {}
MixConverter::MixConverter(const std::vector<tick>& mix_samples, int insert_position)
: mix_samples_(mix_samples), insert_position_(insert_position * 44100 / 1000) {}


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
    {
        samples[i + insert_position_] = static_cast<tick>(std::clamp(
                static_cast<int>(samples[i + insert_position_] + mix_samples_[i]),
                static_cast<int>(MIN_TICK),
                static_cast<int>(MAX_TICK)
        ));
    }

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
            samples[echo_position] = static_cast<tick>(std::clamp(
                    static_cast<int>(samples[echo_position] + repeated_sample * decay_factor),
                    static_cast<int>(MIN_TICK),
                    static_cast<int>(MAX_TICK)
            ));
            decay_factor *= decay_;
        }
    }

    std::cout << "Echo applied successfully" << std::endl;
}