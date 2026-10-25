import wave, numpy as np
REF=r'E:\project\test\keil_keygen\FunkyStars_Original\ref_openmpt.wav'
MINE=r'E:\project\test\keil_keygen\FunkyStars_Original\mine.raw'
w=wave.open(REF,'rb'); sr=w.getframerate()
r=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,2).astype(np.float64).mean(1)
b=np.fromfile(MINE,dtype='<i2').reshape(-1,2).astype(np.float64).mean(1)
n=min(len(r),len(b)); r=r[:n]; b=b[:n]
g=np.sqrt((r**2).mean())/np.sqrt((b**2).mean()); b=b*g

def band(x,lo,hi):
    f=np.fft.rfftfreq(len(x),1/sr); sp=np.abs(np.fft.rfft(x*np.hanning(len(x))))
    m=(f>=lo)&(f<hi); return np.sqrt((sp[m]**2).mean())

for t0 in (22.4, 26.1, 63.0, 123.6, 131.0):
    print('--- %.1f s (40ms 分辨率, 低40-200Hz) ---' % t0)
    print('   t     ref低   mine低   dB      ref全  mine全')
    a=int((t0-0.35)*sr); Wd=int(0.04*sr)
    for k in range(18):
        x=r[a+k*Wd:a+k*Wd+Wd]; y=b[a+k*Wd:a+k*Wd+Wd]
        lo_r=band(x,40,200); lo_b=band(y,40,200)
        print('  %5.2f  %7.0f %7.0f  %+6.1f  %6.0f %6.0f' % (
            t0-0.35+k*0.04, lo_r, lo_b, 20*np.log10((lo_b+1)/(lo_r+1)),
            np.sqrt((x**2).mean()), np.sqrt((y**2).mean())))
    print()
