#ifndef I2C_H
#define I2C_H
#include <stdint.h>
void i2c_init(void);
void max3010x_write_reg(uint8_t reg, uint8_t val);
void max3010x_read(uint8_t reg, uint8_t *buf, uint8_t len);
#endif
