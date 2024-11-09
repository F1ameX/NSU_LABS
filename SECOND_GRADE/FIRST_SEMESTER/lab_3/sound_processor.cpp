#include "sound_processor.h"

SoundProcessor::SoundProcessor(const InputParser& parser) : parser_(parser) {}

bool SoundProcessor::run()
{
    if (parser_.get_input_files().empty())
    {
        std::cerr << "Error: No input files provided." << std::endl;
        return false;
    }

    WAVFile inputFile(parser_.get_input_files().front());
    if (!inputFile.read())
    {
        std::cerr << "Error: Could not read the input WAV file." << std::endl;
        return false;
    }

    std::vector<tick> samples = inputFile.get_samples();
    for (const auto& cmd : parser_.get_mute_commands())
    {
        MuteConverter mute_converter(cmd.start_time, cmd.end_time);
        mute_converter.apply(samples);
    }

    for (const auto& cmd : parser_.get_mix_commands())
    {
        WAVFile additionalFile(cmd.additional_stream);
        if (!additionalFile.read())
        {
            std::cerr << "Error: Could not read the additional stream file for mix command: " << cmd.additional_stream << std::endl;
            return false;
        }
        std::vector<tick> mix_samples = additionalFile.get_samples();

        MixConverter mix_converter(mix_samples, cmd.insert_position);
        mix_converter.apply(samples);
    }

    for (const auto& cmd : parser_.get_echo_commands())
    {
        EchoConverter echo_converter(cmd.delay, cmd.decay);
        echo_converter.apply(samples);
    }

    WAVFile outputFile(parser_.get_output_file_path(), samples, inputFile.get_sample_rate());
    if (!outputFile.write())
    {
        std::cerr << "Error: Could not write to the output WAV file." << std::endl;
        return false;
    }

    std::cout << "Processing complete. Output saved to " << parser_.get_output_file_path() << std::endl;
    return true;
}