#include "WAV_file.h"

WAVFile::WAVFile(const std::string& filepath) : filepath_(filepath), sample_rate_(44100), valid_format_(false) {}
WAVFile::WAVFile(const std::string& filepath, const std::vector<tick>& samples, int sample_rate)
        : filepath_(filepath), samples_(samples), sample_rate_(sample_rate), valid_format_(true) {}
int WAVFile::get_sample_rate() const { return sample_rate_; }
bool WAVFile::is_valid_format() const { return valid_format_; }
const std::vector<tick>& WAVFile::get_samples() const { return samples_; }


bool WAVFile::read()
{
    std::ifstream file(filepath_, std::ios::binary);
    if (!file.is_open())
    {
        std::cerr << "Error! Could not open file: " << filepath_ << std::endl;
        return false;
    }

    if (!read_header(file))
    {
        file.close();
        return false;
    }

    if (!valid_format_)
    {
        std::cerr << "Error! Unsupported WAV format in file: " << filepath_ << std::endl;
        file.close();
        return false;
    }

    tick sample;
    while (file.read(reinterpret_cast<char*>(&sample), sizeof(tick)))
        samples_.push_back(sample);

    if (!file.eof())
    {
        std::cerr << "Error! Unexpected end of file or read error: " << filepath_ << std::endl;
        file.close();
        return false;
    }

    file.close();
    return true;
}


bool WAVFile::write()
{
    std::ofstream file(filepath_, std::ios::binary);
    if (!file.is_open())
    {
        std::cerr << "Error! Could not open file for writing: " << filepath_ << std::endl;
        return false;
    }

    if (!write_header(file))
    {
        file.close();
        return false;
    }

    for (const auto& sample : samples_)
        file.write(reinterpret_cast<const char*>(&sample), sizeof(tick));

    file.close();
    return true;
}


bool WAVFile::read_header(std::ifstream& file)
{
    char chunk_id[4];
    file.read(chunk_id, 4);
    if (std::string(chunk_id, 4) != "RIFF")
    {
        std::cerr << "Error! Not a valid WAV file (missing RIFF header)." << std::endl;
        valid_format_ = false;
        return false;
    }

    uint32_t chunk_size;
    file.read(reinterpret_cast<char*>(&chunk_size), 4);

    char format[4];
    file.read(format, 4);
    if (std::string(format, 4) != "WAVE")
    {
        std::cerr << "Error! Not a valid WAV file (missing WAVE header)." << std::endl;
        valid_format_ = false;
        return false;
    }

    char subchunk1_id[4];
    file.read(subchunk1_id, 4);
    if (std::string(subchunk1_id, 4) != "fmt ")
    {
        std::cerr << "Error! Not a valid WAV file (missing fmt header)." << std::endl;
        valid_format_ = false;
        return false;
    }

    uint32_t subchunk1_size;
    file.read(reinterpret_cast<char*>(&subchunk1_size), 4);
    if (subchunk1_size != 16)
    {
        std::cerr << "Error! Unsupported WAV format (expected PCM)." << std::endl;
        valid_format_ = false;
        return false;
    }

    uint16_t audio_format;
    file.read(reinterpret_cast<char*>(&audio_format), 2);
    if (audio_format != 1)
    {
        std::cerr << "Error! Unsupported audio format (only PCM is supported)." << std::endl;
        valid_format_ = false;
        return false;
    }

    uint16_t num_channels;
    file.read(reinterpret_cast<char*>(&num_channels), 2);
    if (num_channels != 1)
    {
        std::cerr << "Error! Only mono WAV files are supported." << std::endl;
        valid_format_ = false;
        return false;
    }

    uint32_t sample_rate;
    file.read(reinterpret_cast<char*>(&sample_rate), 4);
    if (sample_rate != 44100)
    {
        std::cerr << "Error! Only 44100 Hz sample rate is supported." << std::endl;
        valid_format_ = false;
        return false;
    }
    sample_rate_ = sample_rate;

    uint32_t byte_rate;
    file.read(reinterpret_cast<char*>(&byte_rate), 4);

    uint16_t block_align;
    file.read(reinterpret_cast<char*>(&block_align), 2);

    uint16_t bits_per_sample;
    file.read(reinterpret_cast<char*>(&bits_per_sample), 2);
    if (bits_per_sample != 16)
    {
        std::cerr << "Error! Only 16-bit WAV files are supported." << std::endl;
        return false;
    }

    char subchunk2_id[4];
    file.read(subchunk2_id, 4);
    if (std::string(subchunk2_id, 4) != "data")
    {
        std::cerr << "Error! Missing data header in WAV file." << std::endl;
        return false;
    }

    uint32_t subchunk2_size;
    file.read(reinterpret_cast<char*>(&subchunk2_size), 4);

    valid_format_ = true;
    return true;
}


bool WAVFile::write_header(std::ofstream& file)
{
    uint32_t chunk_size = 36 + samples_.size() * sizeof(tick);
    uint32_t byte_rate = sample_rate_ * 1 * 16 / 8;
    uint16_t block_align = 1 * 16 / 8;
    uint32_t subchunk2_size = samples_.size() * sizeof(tick);

    file.write("RIFF", 4);
    file.write(reinterpret_cast<const char*>(&chunk_size), 4);
    file.write("WAVE", 4);
    if (!file) return false;

    file.write("fmt ", 4);
    uint32_t subchunk1_size = 16;
    uint16_t audio_format = 1;
    uint16_t num_channels = 1;
    uint16_t bits_per_sample = 16;

    file.write(reinterpret_cast<const char*>(&subchunk1_size), 4);
    file.write(reinterpret_cast<const char*>(&audio_format), 2);
    file.write(reinterpret_cast<const char*>(&num_channels), 2);
    file.write(reinterpret_cast<const char*>(&sample_rate_), 4);
    file.write(reinterpret_cast<const char*>(&byte_rate), 4);
    file.write(reinterpret_cast<const char*>(&block_align), 2);
    file.write(reinterpret_cast<const char*>(&bits_per_sample), 2);
    if (!file) return false;

    file.write("data", 4);
    file.write(reinterpret_cast<const char*>(&subchunk2_size), 4);
    if (!file) return false;

    return true;
}