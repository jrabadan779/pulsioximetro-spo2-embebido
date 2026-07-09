/* i2c.c - TWI hardware del ATmega328 a pelo, sin Wire.h.
 * Bus a 400kHz (fast mode). El MAX30102 soporta 400k sin problema, y conviene
 * usarlo: a 100kHz, con promediado x4 y muestreo a 100Hz, el margen para vaciar
 * la FIFO antes de que se llene es ajustado. A 400k queda holgado. */
#include <avr/io.h>
#include "i2c.h"

/* TWBR con prescaler=1: SCL = F_CPU / (16 + 2*TWBR)
 * 16MHz, objetivo 400kHz -> TWBR = 12 exacto. */
#define I2C_TWBR_400K  12
#define MAX3010X_ADDR  0x57

void i2c_init(void) {
    TWSR = 0x00;              /* prescaler 1 */
    TWBR = I2C_TWBR_400K;
    TWCR = (1 << TWEN);
}

static uint8_t i2c_start(void) {
    TWCR = (1 << TWINT) | (1 << TWSTA) | (1 << TWEN);
    while (!(TWCR & (1 << TWINT)));   /* espera al flag, ~us, no delay ciego */
    return (TWSR & 0xF8);
}

static void i2c_stop(void) {
    TWCR = (1 << TWINT) | (1 << TWSTO) | (1 << TWEN);
    while (TWCR & (1 << TWSTO));
}

static uint8_t i2c_write(uint8_t data) {
    TWDR = data;
    TWCR = (1 << TWINT) | (1 << TWEN);
    while (!(TWCR & (1 << TWINT)));
    return (TWSR & 0xF8);
}

static uint8_t i2c_read(uint8_t ack) {
    TWCR = (1 << TWINT) | (1 << TWEN) | (ack ? (1 << TWEA) : 0);
    while (!(TWCR & (1 << TWINT)));
    return TWDR;
}

void max3010x_write_reg(uint8_t reg, uint8_t val) {
    i2c_start();
    i2c_write(MAX3010X_ADDR << 1);   /* SLA+W */
    i2c_write(reg);
    i2c_write(val);
    i2c_stop();
}

/* Lee 'len' bytes desde 'reg'. Importante: hay que usar repeated-start, NO un
 * stop entre la direccion de registro y la lectura, o el sensor pierde el
 * puntero de la FIFO. Es el error clasico con la FIFO del MAX3010x. */
void max3010x_read(uint8_t reg, uint8_t *buf, uint8_t len) {
    i2c_start();
    i2c_write(MAX3010X_ADDR << 1);
    i2c_write(reg);
    i2c_start();                            /* REPEATED start */
    i2c_write((MAX3010X_ADDR << 1) | 1);    /* SLA+R */
    for (uint8_t i = 0; i < len; i++)
        buf[i] = i2c_read(i < (len - 1));   /* ACK menos en el ultimo */
    i2c_stop();
}
