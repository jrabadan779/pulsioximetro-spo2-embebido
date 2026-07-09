import pandas as pd
url = "https://physionet.org/files/pulse-transit-time-ppg/1.1.0/CSV/subjects_info.csv"
df = pd.read_csv(url)
print("COLUMNAS:")
for c in df.columns:
    print("  ", c)
print("\nFILAS:", len(df))
print("\nPRIMERAS 3 FILAS:")
print(df.head(3).to_string())
