#include "game.h"


Game::Game(int field_size) : field_size(field_size), current_iteration(0), game_field(field_size, std::vector<Cell>(field_size)) {}
Game::~Game() = default;

std::vector<std::vector<Cell>>& Game::get_field() { return game_field; }
const std::string& Game::get_universe_name() const {return universe_name;}
const std::string& Game::get_rule() const {return rule; }


void Game::generate_random_universe()
{
    for (std::size_t x = 0; x < field_size; x++)
        for (std::size_t y = 0; y < field_size; y++)
            game_field[x][y].set_current_state(rand() % 2 == 0);
}


bool Game::is_valid_rule(const std::string& rule)
{
    if (rule[0] != 'B' || rule.find('/') == std::string::npos)
        return false;

    size_t slash_pos = rule.find('/');

    if (slash_pos + 1 >= rule.size() || rule[slash_pos + 1] != 'S')
        return false;

    if (slash_pos == 1)
        return false;

    for (size_t i = 1; i < slash_pos; ++i)
        if (rule[i] < '0' || rule[i] > '8')
            return false;

    if (slash_pos + 2 >= rule.size())
        return false;

    for (size_t i = slash_pos + 2; i < rule.size(); ++i)
        if (rule[i] < '0' || rule[i] > '8')
            return false;

    return true;
}


bool Game::prepare_game(const ConsoleParser& parser)
{
    if (parser.is_offline_mode())
    {
        if (parser.get_input_file() == "none")
        {
            std::cout << "Warning: No input file provided. Generating random universe." << std::endl;
            generate_random_universe();
        }
        else
        {
            std::ifstream in_file(parser.get_input_file());
            if (!in_file.is_open())
            {
                std::cerr << "Error: Failed to open file " << parser.get_input_file() << std::endl;
                return false;
            }
            in_file >> *this;
            if (!in_file)
            {
                std::cerr << "Error: Failed to load universe from input file." << std::endl;
                return false;
            }
        }

        if (parser.get_output_file() == "none")
        {
            std::cerr << "Error: No output file specified in offline mode." << std::endl;
            return false;
        }
    }
    else
    {
        if (parser.get_input_file() == "none")
        {
            std::cerr << "Warning: No input file provided. Generating random universe in interactive mode." << std::endl;
            generate_random_universe();
        }
        else
        {
            std::ifstream in_file(parser.get_input_file());
            if (!in_file.is_open())
            {
                std::cerr << "Error: Failed to open file " << parser.get_input_file() << std::endl;
                return false;
            }
            in_file >> *this;
            if (!in_file)
            {
                std::cerr << "Error: Failed to load the universe from file in interactive mode." << std::endl;
                return false;
            }
        }
    }

    if (parser.get_iterations() <= 0)
    {
        std::cerr << "Error: Number of iterations must be greater than zero." << std::endl;
        return false;
    }

    std::cout << "Loaded universe: " << universe_name << std::endl;
    std::cout << "Rule: " << rule << std::endl;
    std::cout << "Game prepared successfully!" << std::endl;

    return true;
}


int Game::count_alive_neighbors(int x, int y) const
{
    int alive_neighbors = 0;
    for (int dx = -1; dx <= 1; ++dx)
    {
        for (int dy = -1; dy <= 1; ++dy)
        {
            if (dx == 0 && dy == 0) continue;
            int nx = (x + dx + field_size) % field_size;
            int ny = (y + dy + field_size) % field_size;
            if (game_field[nx][ny].is_alive()) ++alive_neighbors;
        }
    }
    return alive_neighbors;
}


void Game::run_iteration()
{

    for (int x = 0; x < field_size; ++x)
    {
        for (int y = 0; y < field_size; ++y)
        {
            int alive_neighbors = count_alive_neighbors(x, y);
            bool next_state;

            if (game_field[x][y].is_alive())
                next_state = (alive_neighbors == 2 || alive_neighbors == 3);
            else
                next_state = (alive_neighbors == 3);

            game_field[x][y].set_next_state(next_state);
        }
    }

    for (int x = 0; x < field_size; ++x)
        for (int y = 0; y < field_size; ++y)
            game_field[x][y].apply_next_state();

    ++current_iteration;
}


void Game::display() const
{
    std::cout << "Universe: " << universe_name << ", Rule: " << rule << ", Iteration: " << current_iteration << std::endl;
    for (int x = 0; x < field_size; ++x)
    {
        for (int y = 0; y < field_size; ++y)
            std::cout << (game_field[x][y].is_alive() ? 'O' : '.');
        std::cout << '\n';
    }
}


void Game::run()
{
    std::string command;
    while (true)
    {
        std::cout << "Enter command (tick, dump, exit, help): ";
        std::getline(std::cin, command);
        if (!execute_command(command))
            break;
    }
}


bool Game::execute_command(const std::string& command)
{
    std::istringstream iss(command);
    std::string cmd;
    iss >> cmd;

    if (cmd == "tick" || cmd == "t")
    {
        int iterations = 1;
        if (iss >> iterations)
            run_iterations(iterations);

        else
            run_iterations(1);
        display();
    }

    else if (cmd == "dump")
    {
        std::string filename;
        if (iss >> filename)
        {
            std::ofstream out_file(filename);
            if (out_file.is_open())
            {
                out_file << *this;
                std::cout << "Universe dumped to " << filename << std::endl;
            }
            else
                std::cerr << "Error: Unable to open file " << filename << std::endl;
        }
        else
            std::cerr << "Error: No filename provided for dump command." << std::endl;
    }

    else if (cmd == "exit")
        return false;

    else if (cmd == "help")
        std::cout << "Available commands:\n"
                  << "  tick <n=1> - Perform n iterations (default is 1)\n"
                  << "  dump <filename> - Save the current state to a file\n"
                  << "  exit - End the game\n"
                  << "  help - Show this help message\n";

    else
        std::cerr << "Error: Unknown command." << std::endl;

    return true;
}


void Game::run_iterations(int n)
{
    for (int i = 0; i < n; ++i)
        run_iteration();
}


std::ostream& operator<<(std::ostream& os, const Game& game)
{
    os << "#Life 1.06\n";
    os << "#N " << game.universe_name << "\n";
    os << "#R " << game.rule << "\n";

    for (size_t y = 0; y < game.game_field.size(); ++y)
        for (size_t x = 0; x < game.game_field[y].size(); ++x)
            if (game.game_field[y][x].is_alive())
                os << x << " " << y << "\n";

    return os;
}


std::istream& operator>>(std::istream& is, Game& game)
{
    std::string line;
    bool first_line_checked = false;
    game.universe_name.clear();
    game.rule.clear();

    while (std::getline(is, line))
    {
        if (line.empty()) continue;

        if (line[0] == '#')
        {
            if (!first_line_checked)
            {
                if (line != "#Life 1.06")
                {
                    is.setstate(std::ios::failbit);
                    return is;
                }
                first_line_checked = true;
            }

            if (line.rfind("#N ", 0) == 0)
                game.universe_name = line.substr(3);
            else if (line.rfind("#R ", 0) == 0)
            {
                game.rule = line.substr(3);
                if (!game.is_valid_rule(game.rule))
                {
                    is.setstate(std::ios::failbit);
                    return is;
                }
            }
        }
        else
        {
            std::istringstream coord_stream(line);
            int x, y;
            if (!(coord_stream >> x >> y))
            {
                is.setstate(std::ios::failbit);
                return is;
            }
            if (x >= 0 && y >= 0 && x < game.game_field.size() && y < game.game_field[0].size())
                game.game_field[y][x].set_current_state(true);
            else
            {
                is.setstate(std::ios::failbit);
                return is;
            }
        }
    }

    if (game.universe_name.empty())
        game.universe_name = "Unnamed";

    if (game.rule.empty())
        game.rule = "B3/S23";

    is.clear();
    return is;
}