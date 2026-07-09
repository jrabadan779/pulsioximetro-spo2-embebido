# Compila ambas versiones para ATmega328P y muestra tamaños (Flash=text, SRAM=bss)
MCU = atmega328p
CFLAGS = -mmcu=$(MCU) -Os -DF_CPU=16000000UL

all: sizes

spo2_float.elf: spo2_float.c
	avr-gcc $(CFLAGS) $< -lm -o $@

spo2_fixed.elf: spo2_fixed.c
	avr-gcc $(CFLAGS) $< -o $@

sizes: spo2_float.elf spo2_fixed.elf
	@echo "=== FLOAT (coma flotante) ==="; avr-size spo2_float.elf
	@echo "=== FIXED (punto fijo Q15, buffers int16) ==="; avr-size spo2_fixed.elf

clean:
	rm -f *.elf
