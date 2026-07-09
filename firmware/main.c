/* main.c - Bucle principal 100% no bloqueante.
 * Ni un solo delay() en toda la aplicacion. El ritmo lo marca el Timer1;
 * el main solo reacciona a banderas. Mientras no hay nada que hacer el MCU
 * podria dormir (sleep), lo dejo en busy-wait por simplicidad de depuracion. */
#include <avr/io.h>
#include <avr/interrupt.h>
#include "i2c.h"
#include "timer.h"

/* Config del MAX30102 para modo SpO2. Las corrientes de LED (0x1F ~6.4mA)
 * son un punto de partida; hay que ajustarlas segun el dedo para dejar la
 * DC ~medio rango del ADC. Con dedos frios o piel gruesa toca subir. */
static void max3010x_setup(void) {
    max3010x_write_reg(0x09, 0x40);   /* reset */
    max3010x_write_reg(0x08, 0x4F);   /* FIFO: promedio x4, rollover on */
    max3010x_write_reg(0x09, 0x03);   /* MODE: SpO2 (Red + IR) */
    max3010x_write_reg(0x0A, 0x27);   /* SPO2: ADC 4096nA, 100Hz, 411us */
    max3010x_write_reg(0x0C, 0x1F);   /* LED1 (Red) ~6.4mA */
    max3010x_write_reg(0x0D, 0x1F);   /* LED2 (IR)  ~6.4mA */
}

int main(void) {
    i2c_init();
    max3010x_setup();
    timer1_init_100hz();
    sei();

    for (;;) {
        /* Espera pasiva al tick. No es delay: es "no hagas nada hasta que
         * el timer marque los 10ms". Se cumple 100 veces/seg, ni una mas. */
        if (tick_flag) {
            tick_flag = 0;

            uint8_t buf[6];
            max3010x_read(0x07, buf, 6);   /* FIFO_DATA: 3 bytes/canal */

            uint32_t red = ((uint32_t)buf[0] << 16 | (uint32_t)buf[1] << 8 | buf[2]) & 0x3FFFF;
            uint32_t ir  = ((uint32_t)buf[3] << 16 | (uint32_t)buf[4] << 8 | buf[5]) & 0x3FFFF;

            /* Aqui iria spo2_process(red, ir) del modulo de DSP en punto fijo.
             * (void) para silenciar el warning de no usadas en este esqueleto. */
            (void)red; (void)ir;
        }
        /* main libre para otras tareas (LED de estado, UART...) sin bloquear. */
    }
}
