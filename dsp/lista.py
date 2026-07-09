import wfdb
# Pedir a wfdb la lista real de ficheros publicados del dataset
files = wfdb.get_record_list("pulse-transit-time-ppg/1.1.0")
print("== get_record_list ==")
for f in files[:40]:
    print("  ", f)
print("... total:", len(files))
