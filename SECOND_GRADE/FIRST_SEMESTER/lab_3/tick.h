#ifndef LAB_3_TICK_H
#define LAB_3_TICK_H

using tick = short int;

const tick MAX_TICK = 32767;
const tick MIN_TICK = -32768;

inline tick clamp_tick(tick value)
{
    if (value < MIN_TICK) return MIN_TICK;
    if (value > MAX_TICK) return MAX_TICK;
    return value;
}

#endif