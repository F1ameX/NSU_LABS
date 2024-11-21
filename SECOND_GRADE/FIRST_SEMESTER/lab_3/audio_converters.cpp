#include "audio_converters.h"


MuteConverter::MuteConverter(int start_time, int end_time) : start_time_(start_time), end_time_(end_time)
{
    if (start_time < 0 || end_time < 0)
        throw std::invalid_argument("Start time and end time must be non-negative.");
    if (start_time >= end_time)
        throw std::invalid_argument("Start time must be less than end time.");
}


MixConverter::MixConverter(const std::string& additional_stream, int insert_position)
: additional_stream_(additional_stream), insert_position_(insert_position)
{
    if (insert_position < 0)
        throw std::invalid_argument("Insert position must be non-negative.");

    WAVFile wav_file(additional_stream);
    if (!wav_file.read())
        throw std::runtime_error("Error: Could not read WAV file: " + additional_stream);

    mix_samples_ = wav_file.get_samples();

    if (mix_samples_.empty())
        throw std::runtime_error("Error: WAV file contains no samples: " + additional_stream);
}


EchoConverter::EchoConverter(size_t delay, float decay)
        : delay_(delay), decay_(decay)
{
    if (delay <= 0)
        throw std::invalid_argument("Delay must be positive.");

    if (decay <= 0.0f || decay >= 1.0f)
        throw std::invalid_argument("Decay factor must be in the range (0.0, 1.0).");
}


void MuteConverter::apply(std::vector<tick>& samples)
{
    std::cout << "Applying mute from " << start_time_ << "ms to " << end_time_ << "ms" << std::endl;

    int start_sample = start_time_ * sample_rate / 1000;
    int end_sample = end_time_ * sample_rate / 1000;

    for (size_t i = start_sample; i < end_sample && i < samples.size(); ++i)
        samples[i] = static_cast<tick>(std::clamp(0,
                                                  static_cast<int>(std::numeric_limits<tick>::min()),
                                                  static_cast<int>(std::numeric_limits<tick>::max())
                                                  ));

    std::cout << "Mute applied successfully" << std::endl;
}


void MixConverter::apply(std::vector<tick>& samples)
{
    std::cout << "Applying mix at sample position " << insert_position_ << " ms" << std::endl;

    int sample_position = insert_position_ * sample_rate / 1000;

    if (mix_samples_.empty())
        throw std::runtime_error("Error: The mix samples are empty.");

    if (sample_position < 0 || sample_position >= samples.size())
        throw std::runtime_error("Error: Invalid insert position for mix command.");

    for (size_t i = 0; i < mix_samples_.size() && (i + sample_position) < samples.size(); ++i)
        samples[i + sample_position] = static_cast<tick>(std::clamp(
                static_cast<int>(samples[i + sample_position] + mix_samples_[i]),
                static_cast<int>(std::numeric_limits<tick>::min()),
                static_cast<int>(std::numeric_limits<tick>::max())
        ));

    std::cout << "Mix applied successfully" << std::endl;
}


void EchoConverter::apply(std::vector<tick>& samples)
{
    std::cout << "Applying echo with delay " << delay_ << "ms and decay " << decay_ << std::endl;

    int sample_delay = delay_ * sample_rate / 1000;

    for (size_t i = sample_delay; i < samples.size(); ++i)
    {
        int repeated_sample = samples[i - sample_delay];
        float decay_factor = decay_;

        for (int repeat = 1; repeat <= 5; ++repeat)
        {
            size_t echo_position = i + repeat * sample_delay;
            if (echo_position >= samples.size()) break;

            samples[echo_position] = static_cast<tick>(std::clamp(
                    static_cast<int>(samples[echo_position] + repeated_sample * decay_factor),
                    static_cast<int>(std::numeric_limits<tick>::min()),
                    static_cast<int>(std::numeric_limits<tick>::max())
            ));

            decay_factor *= decay_;
        }
    }
    std::cout << "Echo applied successfully" << std::endl;
}


template <>
std::unique_ptr<AudioConverter> AudioConverterFactory::create_converter<MuteConverter>(const std::vector<std::string>& args)
{
    int start = std::stoi(args[0]);
    int end = std::stoi(args[1]);
    return std::make_unique<MuteConverter>(start, end);
}


template <>
std::unique_ptr<AudioConverter> AudioConverterFactory::create_converter<MixConverter>(const std::vector<std::string>& args)
{
    if (args.size() < 2)
        throw std::invalid_argument("MixConverter requires at least 2 arguments: file_name and insert_position.");


    std::string additional_stream = args[0];
    int insert_position;
    try
    {
        insert_position = std::stoi(args[1]);
    }
    catch (const std::exception& e)
    {
        throw std::invalid_argument("Invalid insert position for mix command: " + std::string(e.what()));
    }

    return std::make_unique<MixConverter>(additional_stream, insert_position);
}


template <>
std::unique_ptr<AudioConverter> AudioConverterFactory::create_converter<EchoConverter>(const std::vector<std::string>& args)
{
    int delay = std::stoi(args[0]);
    float decay = std::stof(args[1]);
    return std::make_unique<EchoConverter>(delay, decay);
}