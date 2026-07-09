#ifndef TIMER_H
#define TIMER_H
#include <stdint.h>
extern volatile uint8_t tick_flag;
void timer1_init_100hz(void);
#endif
