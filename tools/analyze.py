import sys, wave
import numpy as np

REF = r'E:\project\test\keil_keygen\FunkyStars_Original\ref_openmpt.wav'
MINE = r'E:\project\test\keil_keygen\FunkyStars_Original\mine.raw'

w = wave.open(REF,'rb'); sr = w.getframerate()
r = np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,2).astype(np.float64)
b = np.fromfile(MINE,dtype='<i2').reshape(-1,2).astype(np.float64)
n = min(len(r),len(b)); r=r[:n]; b=b[:n]
rr = r.mean(1); bb = b.mean(1)
rr_s = r; bb_s = b

print('=== 电平 ===')
print('ref  RMS %.1f  峰值 %d/%d  削波(>=32767) %d' % (np.sqrt((rr**2).mean()), abs(r[:,0]).max(), abs(r[:,1]).max(), int((np.abs(r)>=32767).sum())))
print('mine RMS %.1f  峰值 %d/%d  削波 %d' % (np.sqrt((bb**2).mean()), abs(b[:,0]).max(), abs(b[:,1]).max(), int((np.abs(b)>=32767).sum())))
g = np.sqrt((rr**2).mean())/np.sqrt((bb**2).mean())
print('归一化增益 %.4f  -> 归一化后 mine 峰值 %.0f' % (g, abs(b).max()*g))
for p in (99.0,99.9,99.99):
    print('  %6.2f%% 分位  ref %.0f  mine(norm) %.0f' % (p, np.percentile(np.abs(rr),p), np.percentile(np.abs(bb),p)*g))

bn = bb*g

print('\n=== 时间对齐 ===')
# 用 100ms RMS 包络做互相关，找最佳偏移
W=sr//10; M=n//W
er=np.array([np.sqrt((rr[i*W:(i+1)*W]**2).mean()) for i in range(M)])
eb=np.array([np.sqrt((bn[i*W:(i+1)*W]**2).mean()) for i in range(M)])
er=(er-er.mean()); eb=(eb-eb.mean())
cc=np.correlate(er,eb,'full')
lag=cc.argmax()-(M-1)
print('最佳包络偏移 %d 个 100ms 窗口 (%+d ms)' % (lag, lag*100))

print('\n=== 归一化后逐 100ms 比值 ===')
rat=np.where(er!=0, eb/(np.sqrt((rr**2).mean())+0*er), 0)
er2=np.array([np.sqrt((rr[i*W:(i+1)*W]**2).mean()) for i in range(M)])
eb2=np.array([np.sqrt((bn[i*W:(i+1)*W]**2).mean()) for i in range(M)])
rat=eb2/(er2+1e-9)
act=np.median(rat); print('中位 %.4f  0.8~1.25 占比 %.2f%%' % (act,100*np.mean((rat>0.8)&(rat<1.25))))
worst=np.argsort(np.abs(np.log(np.maximum(rat,1e-6))))[::-1][:25]
def band(x,lo,hi):
    f=np.fft.rfftfreq(len(x),1/sr); sp=np.abs(np.fft.rfft(x*np.hanning(len(x))))
    m=(f>=lo)&(f<hi); return np.sqrt((sp[m]**2).mean())
print(' 最差窗口:  t(s)   ratio   低40-200  中200-2k  高2k-16k  (dB 差)')
for i in sorted(worst):
    a=i*W; x=rr[a:a+W]; y=bn[a:a+W]
    d=[20*np.log10((band(y,*r_)+1)/(band(x,*r_)+1)) for r_ in [(40,200),(200,2000),(2000,16000)]]
    print('   %6.1f  %6.3f   %+6.2f  %+6.2f  %+6.2f' % (i/10, rat[i], d[0],d[1],d[2]))
