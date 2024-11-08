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


TEST(GameTest, Initialization)
{
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


TEST(GameTest, GenerateRandomUniverse)
{
    Game game(20);
    game.generate_random_universe();

    int alive_count = 0;
    for (int x = 0; x < 20; ++x)
        for (int y = 0; y < 20; ++y)
            if (game.get_field()[x][y].is_alive())
                ++alive_count;

    EXPECT_GT(alive_count, 0);
    EXPECT_LT(alive_count, 400);
}


TEST(GameTest, IsValidRule)
{
    Game game(20);
    EXPECT_TRUE(game.is_valid_rule("B3/S23"));
    EXPECT_TRUE(game.is_valid_rule("B36/S125"));
    EXPECT_FALSE(game.is_valid_rule("B3S23"));
    EXPECT_FALSE(game.is_valid_rule("B9/S23"));
    EXPECT_FALSE(game.is_valid_rule("B3/S"));
}


TEST(GameTest, PrepareGameWithFile)
{
    std::ofstream file("test_universe.txt");
    file << "#Life 1.06\n";
    file << "#N Test Universe\n";
    file << "#R B3/S23\n";
    file << "1 1\n2 2\n3 3\n";
    file.close();

    Game game(20);
    ConsoleParser parser;
    const char* argv[] = {"program", "--file", "test_universe.txt", "--mode", "offline", "--iterations", "10", "--output", "output.txt"};
    ASSERT_TRUE(parser.parse(9, const_cast<char**>(argv)));

    EXPECT_TRUE(game.prepare_game(parser));
    EXPECT_EQ(game.get_universe_name(), "Test Universe");
    EXPECT_EQ(game.get_rule(), "B3/S23");

    std::remove("test_universe.txt");
}

TEST(GameTest, CountAliveNeighbors)
{
    Game game(5);
    game.get_field()[1][1].set_current_state(true);
    game.get_field()[1][2].set_current_state(true);
    game.get_field()[2][1].set_current_state(true);

    EXPECT_EQ(game.count_alive_neighbors(2, 2), 3);
    EXPECT_EQ(game.count_alive_neighbors(0, 0), 1);
}

TEST(GameTest, RunIteration)
{
    Game game(5);
    game.get_field()[1][1].set_current_state(true);
    game.get_field()[1][2].set_current_state(true);
    game.get_field()[2][1].set_current_state(true);

    game.run_iteration();

    EXPECT_TRUE(game.get_field()[2][2].is_alive());
    EXPECT_TRUE(game.get_field()[1][1].is_alive());
}