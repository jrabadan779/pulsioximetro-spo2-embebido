/* timer.c - Timer1 en CTC para tick de muestreo a 100Hz exactos.
 * Prescaler 8 -> tick 0.5us -> OCR1A=19999 da 10.000ms clavados.
 * Probe prescaler 64 (OCR1A=2500), tambien exacto, pero con 8 tengo mas
 * margen de contador por si algun dia bajo el periodo de muestreo. */
#include <avr/io.h>
#include <avr/interrupt.h>
#include "timer.h"

volatile uint8_t tick_flag = 0;

void timer1_init_100hz(void) {
    TCCR1A = 0x00;
    TCCR1B = (1 << WGM12);       /* CTC: TOP = OCR1A */
    OCR1A  = 19999;              /* (16e6/8)/100 - 1 */
    TCCR1B |= (1 << CS11);       /* prescaler 8 -> arranca */
    TIMSK1 = (1 << OCIE1A);
}

/* La ISR es CORTISIMA a proposito: NO lee el sensor ni toca I2C (eso
 * tardaria y podria solaparse con el siguiente tick). Solo levanta una
 * bandera; el trabajo pesado lo hace el main. Asi el disparo es
 * determinista pase lo que pase con el procesado. */
ISR(TIMER1_COMPA_vect) {
    tick_flag = 1;
}
