#include "sound_processor.h"

SoundProcessor::SoundProcessor(const InputParser& parser) : parser_(parser) {}


bool SoundProcessor::run()
{
    try
    {
        if (parser_.get_input_files().empty())
            throw SoundProcessorError("No input files provided");

        WAVFile inputFile(parser_.get_input_files().front());
        if (!inputFile.read())
            throw FileReadError("Could not read the input WAV file");

        std::vector<tick> samples = inputFile.get_samples();

        apply_mute_commands(samples);
        apply_mix_commands(samples);
        apply_echo_commands(samples);

        WAVFile outputFile(parser_.get_output_file_path(), samples, inputFile.get_sample_rate());
        if (!outputFile.write())
            throw FileReadError("Could not write to the output WAV file");

        std::cout << "Processing complete. Output saved to " << parser_.get_output_file_path() << std::endl;
        return true;
    }

    catch (const SoundProcessorError& e)
    {
        std::cerr << "Error: " << e.what() << std::endl;
        return false;
    }

    catch (const ConfigParseError& e)
    {
        std::cerr << "Configuration Error: " << e.what() << std::endl;
        return false;
    }
}


void SoundProcessor::apply_mute_commands(std::vector<tick>& samples)
{
    for (const auto& cmd : parser_.get_mute_commands())
    {
        MuteConverter mute_converter(cmd.start_time, cmd.end_time);
        mute_converter.apply(samples);
    }
}


bool SoundProcessor::apply_mix_commands(std::vector<tick>& samples)
{
    for (const auto& cmd : parser_.get_mix_commands())
    {
        WAVFile additionalFile(cmd.additional_stream);
        if (!additionalFile.read())
        {
            std::cerr << "Error: Could not read the additional stream file for mix command: "
                      << cmd.additional_stream << std::endl;
            return false;
        }

        std::vector<tick> mix_samples = additionalFile.get_samples();
        if (mix_samples.empty())
        {
            std::cerr << "Warning: Additional stream for mix command is empty: "
                      << cmd.additional_stream << std::endl;
            continue;
        }

        MixConverter mix_converter(mix_samples, cmd.insert_position);
        mix_converter.apply(samples);
    }
    return true;
}

void SoundProcessor::apply_echo_commands(std::vector<tick>& samples)
{
    for (const auto& cmd : parser_.get_echo_commands())
    {
        EchoConverter echo_converter(cmd.delay, cmd.decay);
        echo_converter.apply(samples);
    }
}