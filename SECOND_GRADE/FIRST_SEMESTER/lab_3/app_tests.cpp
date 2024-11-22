#include "gtest/gtest.h"
#include "input_parser.h"
#include "sound_processor.h"
#include "exceptions.h"


TEST(InputParserTest, ParseArguments)
{
    int argc = 5;
    char* argv[] = { "./sound_processor", "-c", "config.txt", "output.wav", "input.wav" };

    InputParser parser(argc, argv);

    ASSERT_TRUE(parser.parse());
    EXPECT_EQ(parser.get_config_file_path(), "config.txt");
    EXPECT_EQ(parser.get_output_file_path(), "output.wav");
    EXPECT_EQ(parser.get_input_files().front(), "input.wav");
}


TEST(InputParserTest, ParseHelpFlag)
{
    int argc = 2;
    char* argv[] = { "./sound_processor", "-h" };

    InputParser parser(argc, argv);

    ASSERT_TRUE(parser.parse());
    EXPECT_TRUE(parser.show_help());
}


TEST(SoundProcessorTest, Initialization)
{
    int argc = 5;
    char* argv[] = { "./sound_processor", "-c", "config.txt", "output.wav", "input.wav" };

    InputParser parser(argc, argv);
    ASSERT_TRUE(parser.parse());

    SoundProcessor processor(parser);
    EXPECT_NO_THROW(processor.run());
}


TEST(InputParserTest, InvalidArguments)
{
    int argc = 3;
    char* argv[] = { "./sound_processor", "-x", "config.txt" };

    InputParser parser(argc, argv);

    EXPECT_FALSE(parser.parse());
}


TEST(InputParserTest, EmptyConfigFile)
{
    int argc = 5;
    char* argv[] = { "./sound_processor", "-c", "test_config_empty.txt", "output.wav", "input.wav" };
    InputParser parser(argc, argv);

    ASSERT_TRUE(parser.parse());
    EXPECT_TRUE(parser.get_mute_commands().empty());
    EXPECT_TRUE(parser.get_mix_commands().empty());
    EXPECT_TRUE(parser.get_echo_commands().empty());
}


TEST(InputParserTest, InvalidConfigCommand)
{
    int argc = 5;
    char* argv[] = { "./sound_processor", "-c", "test_config_invalid.txt", "output.wav", "input.wav" };
    InputParser parser(argc, argv);

    EXPECT_THROW(parser.parse(), std::invalid_argument);
}


TEST(InputParserTest, InvalidMuteCommand)
{
    int argc = 5;
    char* argv[] = { "./sound_processor", "-c", "test_config_invalid_mute.txt", "output.wav", "input.wav" };
    InputParser parser(argc, argv);

    EXPECT_THROW(parser.parse(), std::invalid_argument);
}


TEST(InputParserTest, InvalidEchoCommand)
{
    int argc = 5;
    char* argv[] = { "./sound_processor", "-c", "test_config_invalid_echo.txt", "output.wav", "input.wav" };
    InputParser parser(argc, argv);

    EXPECT_THROW(parser.parse(), std::invalid_argument);
}


TEST(SoundProcessorTest, RunWithNoCommands)
{
    int argc = 5;
    char* argv[] = { "./sound_processor", "-c", "test_config_empty.txt", "output.wav", "input.wav" };

    InputParser parser(argc, argv);
    ASSERT_TRUE(parser.parse());

    SoundProcessor processor(parser);
    EXPECT_NO_THROW(processor.run());
}


TEST(InputParserTest, MissingRequiredArguments)
{
    int argc = 2;
    char* argv[] = { "./sound_processor", "-c" };

    InputParser parser(argc, argv);

    EXPECT_FALSE(parser.parse());
}


TEST(InputParserTest, NonexistentConfigFile)
{
    int argc = 5;
    char* argv[] = { "./sound_processor", "-c", "nonexistent_config.txt", "output.wav", "input.wav" };
    InputParser parser(argc, argv);

    EXPECT_THROW(parser.parse(), FileReadError);
}