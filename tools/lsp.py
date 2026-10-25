import wave, numpy as np
REF=r'E:\project\test\keil_keygen\FunkyStars_Original\ref_openmpt.wav'
MINE=r'E:\project\test\keil_keygen\FunkyStars_Original\mine.raw'
w=wave.open(REF,'rb'); sr=w.getframerate()
r=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,2).astype(np.float64).mean(1)
b=np.fromfile(MINE,dtype='<i2').reshape(-1,2).astype(np.float64).mean(1)
n=min(len(r),len(b)); r=r[:n]; b=b[:n]
print('DC: ref %+.1f  mine %+.1f' % (r.mean(), b.mean()))
print('静音段(最后0.5s) RMS: ref %.1f mine %.1f' % (np.sqrt((r[-22050:]**2).mean()), np.sqrt((b[-22050:]**2).mean())))

NS=4096
def lsp(x,y):
    wx=np.hanning(len(x))
    fx=np.abs(np.fft.rfft(x*wx)); fy=np.abs(np.fft.rfft(y*wx))
    fx[0]=0; fy[0]=0
    m=fx>fx.max()*3e-4          # 只在 ref 有信号的频点比
    if m.sum()<20: return np.nan
    a=20*np.log10(fx[m]); c=20*np.log10(np.maximum(fy[m],1e-3))
    a-=a.mean(); c-=c.mean()     # 去掉整体斜率无关的常数
    return np.sqrt(np.mean((a-c)**2))

hop=sr//10
ts=[];ds=[]
for a0 in range(0, n-NS, hop):
    v=lsp(r[a0:a0+NS], b[a0:a0+NS])
    if not np.isnan(v): ts.append((a0+NS/2)/sr); ds.append(v)
ts=np.array(ts); ds=np.array(ds)
print('对数频谱形态距离: 中位 %.4f  均值 %.4f  95分位 %.4f  最大 %.4f (t=%.1fs)' %
      (np.median(ds), ds.mean(), np.percentile(ds,95), ds.max(), ts[ds.argmax()]))
worst=np.argsort(ds)[::-1][:15]
print('最差:', ['%.1f(%.2f)'%(ts[i],ds[i]) for i in sorted(worst)])
