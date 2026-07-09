import wfdb
# Cargar la cabecera de un registro y volcar TODO: comentarios y metadatos
rec = wfdb.rdheader("s1_sit", pn_dir="pulse-transit-time-ppg/1.1.0")
print("== COMMENTS (aqui suelen ir los numericos: SpO2, HR, BP) ==")
for c in rec.comments:
    print("  ", c)
print("\n== signal names ==")
print(rec.sig_name)
