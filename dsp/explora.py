import wfdb, numpy as np, matplotlib.pyplot as plt

# Descarga y carga un registro del dataset directamente del servidor PhysioNet
rec = wfdb.rdrecord("s1_sit",
                    pn_dir="pulse-transit-time-ppg/1.1.0",
                    channel_names=["pleth_1", "pleth_2"])
fs = rec.fs
red = rec.p_signal[:, 0]
ir  = rec.p_signal[:, 1]
print("OK - registro cargado")
print("fs =", fs, "Hz | muestras =", len(red), "| duracion =", round(len(red)/fs/60,1), "min")
print("red: min/max =", round(red.min(),1), "/", round(red.max(),1))
print("ir : min/max =", round(ir.min(),1),  "/", round(ir.max(),1))

# Plotear 10 s para ver el pulso
n = int(10*fs)
t = np.arange(n)/fs
plt.figure(figsize=(10,4))
plt.plot(t, red[:n], label="pleth_1 (rojo)", color="red", lw=0.8)
plt.plot(t, ir[:n],  label="pleth_2 (IR)",  color="darkred", lw=0.8)
plt.xlabel("Tiempo (s)"); plt.ylabel("PPG (u.a.)")
plt.title("PPG crudo - dataset PTT-PPG (s1_sit, 10 s)")
plt.legend(); plt.grid(alpha=0.3); plt.tight_layout()
plt.savefig("media/ppg_crudo.png", dpi=130)
print("guardado media/ppg_crudo.png")
