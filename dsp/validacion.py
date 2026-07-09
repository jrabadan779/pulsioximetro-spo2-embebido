"""Valida el algoritmo ratio-of-ratios (punto fijo Q15) contra la referencia
clinica del dataset PhysioNet PTT-PPG. Recorre los 66 registros, decima
500->100 Hz, aplica el mismo pipeline que el firmware (filtro 5Hz 2o orden +
DC/AC + ratio) y compara la SpO2 estimada con spo2_start/end de cada cabecera."""
import wfdb, numpy as np, matplotlib.pyplot as plt, re, time
from scipy.signal import decimate

DB = "pulse-transit-time-ppg/1.1.0"
FS_IN, FS_OUT = 500, 100
DECIM = FS_IN // FS_OUT
A_LP_Q15, A_DC_Q15, Q = 7833, 328, 15   # identicos a spo2_fixed.c
def mulq(a, x): return (a * x) >> Q

def ratio_of_ratios(red, ir):
    dc_r=dc_ir=lp1r=lp2r=lp1i=lp2i=0
    acr=[]; aci=[]; dcrh=[]; dcih=[]
    for xr, xi in zip(red.astype(np.int64), ir.astype(np.int64)):
        dc_r += mulq(A_DC_Q15, xr-dc_r); dc_ir += mulq(A_DC_Q15, xi-dc_ir)
        lp1r += mulq(A_LP_Q15, xr-lp1r); lp2r += mulq(A_LP_Q15, lp1r-lp2r)
        lp1i += mulq(A_LP_Q15, xi-lp1i); lp2i += mulq(A_LP_Q15, lp1i-lp2i)
        acr.append((lp2r-dc_r)**2); aci.append((lp2i-dc_ir)**2)
        dcrh.append(dc_r); dcih.append(dc_ir)
    s = 5*FS_OUT
    ACr=np.sqrt(np.mean(acr[s:])); ACi=np.sqrt(np.mean(aci[s:]))
    DCr=np.mean(dcrh[s:]); DCi=np.mean(dcih[s:])
    if DCr==0 or DCi==0 or ACi==0: return None
    return (ACr/DCr)/(ACi/DCi)

def load_retry(fn, *a, **k):
    for att in range(4):
        try: return fn(*a, **k)
        except Exception:
            if att==3: raise
            time.sleep(2*(att+1))

def to_int(x):
    x = x - x.min(); x = x/(x.max()+1e-9)*200000 + 30000
    return x.astype(np.int64)

records = wfdb.get_record_list(DB)
res = {"sit":[], "walk":[], "run":[]}
for rec_name in records:
    act = rec_name.split("_")[1]
    try:
        hea = load_retry(wfdb.rdheader, rec_name, pn_dir=DB)
        comm = " ".join(hea.comments)
        s0 = re.search(r"<spo2_start>:\s*(\d+)", comm)
        s1 = re.search(r"<spo2_end>:\s*(\d+)", comm)
        if not s0 or not s1: continue
        ref = (int(s0.group(1))+int(s1.group(1)))/2.0
        rec = load_retry(wfdb.rdrecord, rec_name, pn_dir=DB, channel_names=["pleth_1","pleth_2"])
        red, ir = rec.p_signal[:,0], rec.p_signal[:,1]
        m = ~(np.isnan(red)|np.isnan(ir)); red, ir = red[m], ir[m]
        if len(red) < FS_IN*30: continue
        red = decimate(red, DECIM, ftype="fir"); ir = decimate(ir, DECIM, ftype="fir")
        R = ratio_of_ratios(to_int(red), to_int(ir))
        if R is None: continue
        est = max(70, min(100, 110.0 - 25.0*abs(R)))
        res[act].append((ref, est))
        print(f"{rec_name:10s} [{act:4s}] ref={ref:5.1f}  est={est:5.1f}")
    except Exception as e:
        print(f"{rec_name}: ERROR {e}")

def stats(name, data):
    if not data: return
    a=np.array(data); err=np.abs(a[:,1]-a[:,0])
    print(f"[{name}] n={len(a)}  MAE={err.mean():.2f}%  RMSE={np.sqrt(np.mean((a[:,1]-a[:,0])**2)):.2f}%  max={err.max():.2f}%")

print("\n===== RESULTADOS POR ACTIVIDAD =====")
stats("SIT", res["sit"]); stats("WALK", res["walk"]); stats("RUN", res["run"])
stats("TODOS", res["sit"]+res["walk"]+res["run"])

if res["sit"]:
    a=np.array(res["sit"]); ref,est=a[:,0],a[:,1]; err=np.abs(est-ref)
    plt.figure(figsize=(7,7))
    plt.scatter(ref,est,alpha=0.6,color="#2563eb",label="sit")
    plt.plot([90,101],[90,101],"--",color="#64748b",label="ideal")
    plt.xlabel("SpO2 referencia (%)"); plt.ylabel("SpO2 estimada (%)")
    plt.title(f"Validacion SpO2 en reposo vs PhysioNet\nMAE={err.mean():.2f}%  (n={len(a)})")
    plt.legend(); plt.grid(alpha=0.3); plt.tight_layout()
    plt.savefig("media/validacion_spo2.png", dpi=130)
