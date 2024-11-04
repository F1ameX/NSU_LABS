#include "cell.h"
#include "console_parser.h"
#include "game.h"
#include "gtest/gtest.h"


TEST(CellTest, InitialState)
{
    Cell cell;
    EXPECT_FALSE(cell.is_alive());
}


TEST(CellTest, StateTransitions)
{
    Cell cell;
    cell.set_current_state(true);
    EXPECT_TRUE(cell.is_alive());

    cell.set_next_state(false);
    cell.apply_next_state();
    EXPECT_FALSE(cell.is_alive());
}


TEST(ConsoleParserTest, ParseHelpFlag)
{
    const char* argv[] = {"program", "--help"};
    ConsoleParser parser;
    parser.parse(2, const_cast<char**>(argv));
    EXPECT_TRUE(parser.help_requested());
}


TEST(ConsoleParserTest, ParseFileFlag)
{
    const char* argv[] = {"program", "--file", "input.txt"};
    ConsoleParser parser;
    EXPECT_TRUE(parser.parse(3, const_cast<char**>(argv)));
    EXPECT_EQ(parser.get_input_file(), "input.txt");
}


TEST(ConsoleParserTest, ParseModeFlag)
{
    const char* argv[] = {"program", "--mode", "offline"};
    ConsoleParser parser;
    EXPECT_TRUE(parser.parse(3, const_cast<char**>(argv)));
    EXPECT_TRUE(parser.is_offline_mode());
}


TEST(GameTest, Initialization) {
    Game game(10);
    EXPECT_EQ(game.get_field().size(), 10);
    EXPECT_EQ(game.get_field()[0].size(), 10);
    EXPECT_EQ(game.get_universe_name(), "");
    EXPECT_EQ(game.get_rule(), "");
}


TEST(GameTest, PrepareGameOfflineMode)
{
    Game game(5);
    ConsoleParser parser;
    const char* argv[] = {"program", "--file", "input.txt", "--mode", "offline", "--iterations", "10", "--output", "output.txt"};
    ASSERT_TRUE(parser.parse(9, const_cast<char**>(argv)));

    EXPECT_TRUE(game.prepare_game(parser));
    EXPECT_EQ(game.get_universe_name(), "Blinker Oscillator");
    EXPECT_EQ(game.get_rule(), "B3/S23");
}


TEST(GameTest, RunMultipleIterations)
{
    Game game(5);
    ConsoleParser parser;
    const char* argv[] = {"program", "--iterations", "3"};
    ASSERT_TRUE(parser.parse(3, const_cast<char**>(argv)));

    game.run_iterations(parser.get_iterations());

    EXPECT_NO_THROW(game.run_iterations(parser.get_iterations()));
}