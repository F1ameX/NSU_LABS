#include "gtest/gtest.h"
#include "input_parser.h"
#include "sound_processor.h"


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


TEST(InputParserTest, ParseMuteCommand)
{
    char* argv[] = { "./sound_processor", "-c", "test_config_mute.txt", "output.wav", "input.wav" };
    int argc = 5;
    InputParser parser(argc, argv);

    ASSERT_TRUE(parser.parse());

    auto mute_commands = parser.get_mute_commands();
    ASSERT_EQ(mute_commands.size(), 1);
    EXPECT_EQ(mute_commands[0].start_time, 0);
    EXPECT_EQ(mute_commands[0].end_time, 1000);
}


TEST(InputParserTest, ParseMixCommand)
{
    char* argv[] = { "./sound_processor", "-c", "test_config_mix.txt", "output.wav", "input.wav" };
    int argc = 5;
    InputParser parser(argc, argv);

    ASSERT_TRUE(parser.parse());

    auto mix_commands = parser.get_mix_commands();
    ASSERT_EQ(mix_commands.size(), 1);
    EXPECT_EQ(mix_commands[0].additional_stream, "district_four.wav");
    EXPECT_EQ(mix_commands[0].insert_position, 500);
}


TEST(InputParserTest, ParseEchoCommand)
{
    char* argv[] = { "./sound_processor", "-c", "test_config_echo.txt", "output.wav", "input.wav" };
    int argc = 5;
    InputParser parser(argc, argv);

    ASSERT_TRUE(parser.parse());

    auto echo_commands = parser.get_echo_commands();
    ASSERT_EQ(echo_commands.size(), 1);
    EXPECT_EQ(echo_commands[0].delay, 300);
    EXPECT_FLOAT_EQ(echo_commands[0].decay, 0.5);
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
    char* argv[] = { "./sound_processor", "-c", "test_config_empty.txt", "output.wav", "input.wav" };
    int argc = 5;
    InputParser parser(argc, argv);

    EXPECT_TRUE(parser.parse());
    EXPECT_TRUE(parser.get_mute_commands().empty());
    EXPECT_TRUE(parser.get_mix_commands().empty());
    EXPECT_TRUE(parser.get_echo_commands().empty());
}


TEST(InputParserTest, InvalidConfigCommand)
{
    char* argv[] = { "./sound_processor", "-c", "test_config_invalid.txt", "output.wav", "input.wav" };
    int argc = 5;
    InputParser parser(argc, argv);

    EXPECT_FALSE(parser.parse());
}


TEST(InputParserTest, InvalidMuteCommand)
{
    char* argv[] = { "./sound_processor", "-c", "test_config_invalid_mute.txt", "output.wav", "input.wav" };
    int argc = 5;
    InputParser parser(argc, argv);

    EXPECT_FALSE(parser.parse());
}

TEST(InputParserTest, InvalidEchoCommand)
{
    char* argv[] = { "./sound_processor", "-c", "test_config_invalid_echo.txt", "output.wav", "input.wav" };
    int argc = 5;
    InputParser parser(argc, argv);

    EXPECT_FALSE(parser.parse());
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
    char* argv[] = { "./sound_processor", "-c", "nonexistent_config.txt", "output.wav", "input.wav" };
    int argc = 5;
    InputParser parser(argc, argv);

    EXPECT_THROW(parser.parse(), FileReadError);
}