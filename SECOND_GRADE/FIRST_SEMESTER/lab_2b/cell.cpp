#include "cell.h"

Cell::Cell() : current_state(false), next_state(false) {}
bool Cell::is_alive() const {return current_state;}
void Cell::set_current_state(bool state) {current_state = state;}
void Cell::set_next_state(bool state) {next_state = state;}
void Cell::apply_next_state() {current_state = next_state;}