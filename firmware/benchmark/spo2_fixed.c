#include <stdint.h>
#define N 128
/* buffers int16 en vez de float/int32 -> mitad de SRAM */
static int16_t bufr[N], bufir[N]; static uint8_t idx=0;
static int32_t dc_r=0, dc_ir=0;
#define A_DC_Q15 328
#define Q 15
static inline int32_t mulq(int32_t a,int32_t x){ return (int32_t)(((int64_t)a*x)>>Q); }
static uint32_t isqrt32(uint32_t v){ /* sqrt entera 32-bit, mas compacta */
    uint32_t rem=0, root=0; for(int i=0;i<16;i++){ root<<=1; rem=(rem<<2)|(v>>30); v<<=2; root++;
    if(root<=rem){rem-=root;root++;}else root--; } return root>>1; }
int16_t process(uint32_t red, uint32_t ir){
    int32_t r=(int32_t)red, i=(int32_t)ir;
    dc_r += mulq(A_DC_Q15, r-dc_r); dc_ir += mulq(A_DC_Q15, i-dc_ir);
    /* AC cabe en int16 (es ~1-2% de la DC) */
    bufr[idx]=(int16_t)(r-dc_r); bufir[idx]=(int16_t)(i-dc_ir); idx=(idx+1)%N;
    uint32_t sr=0, si=0;
    for(uint8_t k=0;k<N;k++){ sr+=(int32_t)bufr[k]*bufr[k]; si+=(int32_t)bufir[k]*bufir[k]; }
    int32_t ac_r=isqrt32(sr/N), ac_ir=isqrt32(si/N);
    if(dc_r==0||dc_ir==0||ac_ir==0) return 0;
    int64_t num=(int64_t)ac_r*(dc_ir<0?-dc_ir:dc_ir);
    int64_t den=(int64_t)(dc_r<0?-dc_r:dc_r)*ac_ir;
    if(den==0) return 0;
    int32_t R_q=(int32_t)((num<<Q)/den);
    return (int16_t)((((int32_t)110<<Q)-25*R_q)>>Q);
}
volatile uint32_t g_r,g_ir; volatile int16_t g_o;
int main(void){ for(;;) g_o=process(g_r,g_ir); }
