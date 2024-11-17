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

        if (!apply_commands(samples))
        {
            std::cerr << "Error occurred while applying commands, exiting." << std::endl;
            return false;
        }

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


bool SoundProcessor::apply_commands(std::vector<tick>& samples)
{
    try
    {

        for (const auto& converter : parser_.get_mute_commands())
            converter->apply(samples);

        for (const auto& converter : parser_.get_mix_commands())
            converter->apply(samples);

        for (const auto& converter : parser_.get_echo_commands())
            converter->apply(samples);

        return true;
    }
    catch (const std::exception& e)
    {
        std::cerr << "Error applying commands: " << e.what() << std::endl;
        return false;
    }
}