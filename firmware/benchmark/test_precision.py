import numpy as np, subprocess, textwrap, os

# Genero PPG sintetico: DC grande + AC pulsatil, para Red e IR, con un R conocido.
fs=100; T=20; t=np.arange(0,T,1/fs)
hr=1.2 # Hz (~72 bpm)
# R objetivo ~0.6 -> SpO2 = 110-25*0.6 = 95%
DC_r, DC_ir = 100000.0, 120000.0
# AC/DC: para R=0.6 -> (ACr/DCr)/(ACir/DCir)=0.6
perf_ir=0.02
perf_r=0.6*perf_ir
AC_r=DC_r*perf_r; AC_ir=DC_ir*perf_ir
puls=np.sin(2*np.pi*hr*t)
red = DC_r + AC_r*puls + np.random.normal(0,20,len(t))
ir  = DC_ir + AC_ir*puls + np.random.normal(0,20,len(t))
red=np.clip(red,0,262143).astype(np.uint32)
ir =np.clip(ir ,0,262143).astype(np.uint32)

# Genero un C driver que corre float y fixed sobre las mismas muestras
samples = ",".join(f"{{{r},{i}}}" for r,i in zip(red,ir))
driver = textwrap.dedent(f"""
#include <stdint.h>
#include <stdio.h>
#include <math.h>
#define N 128
/* ---- FLOAT ---- */
static float bufr[N],bufir[N]; static uint8_t idx=0; static float dcr=0,dcir=0;
float pf(uint32_t red,uint32_t ir){{ float r=red,i=ir; dcr+=0.01f*(r-dcr);dcir+=0.01f*(i-dcir);
 bufr[idx]=r-dcr;bufir[idx]=i-dcir;idx=(idx+1)%N; float sr=0,si=0;
 for(int k=0;k<N;k++){{sr+=bufr[k]*bufr[k];si+=bufir[k]*bufir[k];}}
 float ar=sqrtf(sr/N),ai=sqrtf(si/N); if(!dcr||!dcir||!ai)return 0;
 float R=(ar/dcr)/(ai/dcir); return 110.0f-25.0f*R; }}
/* ---- FIXED int16 ---- */
static int16_t br[N],bi[N]; static uint8_t ix=0; static int32_t Dr=0,Di=0;
#define Q 15
static int32_t mq(int32_t a,int32_t x){{return (int32_t)(((int64_t)a*x)>>Q);}}
static uint32_t isq(uint32_t v){{uint32_t rem=0,root=0;for(int i=0;i<16;i++){{root<<=1;rem=(rem<<2)|(v>>30);v<<=2;root++;if(root<=rem){{rem-=root;root++;}}else root--;}}return root>>1;}}
int16_t px(uint32_t red,uint32_t ir){{ int32_t r=red,i=ir; Dr+=mq(328,r-Dr);Di+=mq(328,i-Di);
 br[ix]=(int16_t)(r-Dr);bi[ix]=(int16_t)(i-Di);ix=(ix+1)%N; uint32_t sr=0,si=0;
 for(int k=0;k<N;k++){{sr+=(int32_t)br[k]*br[k];si+=(int32_t)bi[k]*bi[k];}}
 int32_t ar=isq(sr/N),ai=isq(si/N); if(!Dr||!Di||!ai)return 0;
 int64_t num=(int64_t)ar*(Di<0?-Di:Di),den=(int64_t)(Dr<0?-Dr:Dr)*ai; if(!den)return 0;
 int32_t Rq=(int32_t)((num<<Q)/den); return (int16_t)((((int32_t)110<<Q)-25*Rq)>>Q); }}
uint32_t RED[]={{ {",".join(map(str,red))} }};
uint32_t IR[]={{ {",".join(map(str,ir))} }};
int main(void){{ int n=sizeof(RED)/4; float lf=0; int li=0;
 for(int k=0;k<n;k++){{ lf=pf(RED[k],IR[k]); li=px(RED[k],IR[k]); }}
 printf("%.4f %d\\n", lf, li); return 0; }}
""")
open("cmp.c","w").write(driver)
subprocess.run(["gcc","cmp.c","-lm","-o","cmp"],check=True)
out=subprocess.check_output(["./cmp"]).decode().split()
sf,si=float(out[0]),int(out[1])
print(f"SpO2 objetivo (sintetico): 95.0 %")
print(f"SpO2 version FLOAT       : {sf:.2f} %")
print(f"SpO2 version FIXED int16 : {si} %")
print(f"Diferencia fixed vs float: {abs(sf-si):.2f} puntos porcentuales")
