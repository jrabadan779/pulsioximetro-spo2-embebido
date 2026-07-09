#include <stdint.h>
#include <math.h>
#define N 128
static float bufr[N], bufir[N]; static uint8_t idx=0;
static float dc_r=0, dc_ir=0;
#define A_DC 0.01f
float process(uint32_t red, uint32_t ir){
    float r=(float)red, i=(float)ir;
    dc_r += A_DC*(r-dc_r); dc_ir += A_DC*(i-dc_ir);
    bufr[idx]=r-dc_r; bufir[idx]=i-dc_ir; idx=(idx+1)%N;
    /* RMS de la AC sobre la ventana */
    float sr=0, si=0;
    for(uint8_t k=0;k<N;k++){ sr+=bufr[k]*bufr[k]; si+=bufir[k]*bufir[k]; }
    float ac_r=sqrtf(sr/N), ac_ir=sqrtf(si/N);
    if(dc_r==0||dc_ir==0||ac_ir==0) return 0;
    float R=(ac_r/dc_r)/(ac_ir/dc_ir);
    return 110.0f - 25.0f*R;
}
volatile uint32_t g_r,g_ir; volatile float g_o;
int main(void){ for(;;) g_o=process(g_r,g_ir); }
