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

        for (const auto& converter : parser_.get_audio_commands())
        {
            std::cout << "Applying command..." << std::endl;
            converter->apply(samples);
        }

        WAVFile outputFile(parser_.get_output_file_path(), samples, inputFile.get_sample_rate());
        std::cout << "Writing to output file: " << parser_.get_output_file_path() << std::endl;

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