#pragma once

class Cell {
private:
    bool current_state;
    bool next_state;
public:
    Cell();

    void apply_next_state();
    [[nodiscard]] bool is_alive() const;
    void set_current_state(bool state);
    void set_next_state(bool state);

};

