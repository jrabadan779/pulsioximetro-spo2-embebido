# Benchmark punto fijo vs coma flotante (ATmega328P)

Comparación de la implementación del algoritmo ratio-of-ratios en coma flotante
(`spo2_float.c`) frente a punto fijo Q15 con buffers int16 (`spo2_fixed.c`).

## Reproducir

Tamaño (requiere `gcc-avr` y `avr-libc`):

```
make sizes
```

Precisión (requiere `gcc` y `python3` con numpy):

```
python3 test_precision.py
```

## Resultados medidos (avr-gcc 7.3, -Os)

| Métrica       | Float  | Fixed (int16 Q15) | Reducción |
|---------------|--------|-------------------|-----------|
| Flash (text)  | 2086 B | 1808 B            | -13.3%    |
| SRAM (bss)    | 1045 B |  531 B            | -49.2%    |
| Error vs float| -      | -                 | ~0.01 pp  |

## Nota de diseño

El ahorro de SRAM no viene de "usar punto fijo" sin más, sino de una decisión
concreta: almacenar la componente AC en `int16` en lugar de `float`/`int32`.
La AC es ~1-2% de la DC, así que cabe de sobra en 16 bits sin pérdida relevante.
Una primera versión con buffers `int32` + raíz entera resultaba MÁS grande en
Flash que la versión float; el punto fijo es lo que habilita usar int16 sin
degradar la precisión (verificado: 0.01 puntos porcentuales frente a float).
