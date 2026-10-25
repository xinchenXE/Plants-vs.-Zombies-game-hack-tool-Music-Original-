import wave, numpy as np, struct, sys

def load_wav(path):
    w = wave.open(path,'rb')
    n = w.getnframes(); ch = w.getnchannels(); sw = w.getsampwidth()
    raw = w.readframes(n); w.close()
    a = np.frombuffer(raw, dtype='<i2').astype(np.float64)/32768.0
    a = a.reshape(-1, ch).mean(axis=1)
    return a, w.getframerate()

def env_at(x, sr, f0, win=0.08, hop=0.01):
    """complex demodulation envelope at f0"""
    n_win = int(win*sr); n_hop = int(hop*sr)
    t = np.arange(len(x))/sr
    z = x*np.exp(-2j*np.pi*f0*t)
    out_t=[]; out_m=[]
    k=0
    while k+n_win <= len(z):
        seg = z[k:k+n_win]
        out_m.append(abs(seg.mean()))
        out_t.append((k+n_win/2)/sr)
        k += n_hop
    return np.array(out_t), np.array(out_m)

ref, sr = load_wav(r'E:\project\test\keil_keygen\FunkyStars_Original\ref_openmpt.wav')
_m = np.frombuffer(open(r'E:\project\test\keil_keygen\FunkyStars_Original\mine.raw','rb').read(), dtype='<i2').astype(np.float64)/32768.0
mine = _m.reshape(-1,2).mean(axis=1)
print('sr', sr, 'ref len', len(ref)/sr, 'mine len', len(mine)/sr,
      'ref rms', round(np.sqrt((ref**2).mean())*32768,1), 'mine rms', round(np.sqrt((mine**2).mean())*32768,1))

# 先确认 25.5-27.0 区间参考里的低频峰值位置
s=25.5; e=27.0
seg = ref[int(s*sr):int(e*sr)]
W = int(0.5*sr)
sp = np.abs(np.fft.rfft(seg*np.hanning(len(seg))))
fr = np.fft.rfftfreq(len(seg), 1/sr)
sel = (fr>30)&(fr<120)
top = np.argsort(sp[sel])[::-1][:8]
print('低频峰值 (Hz, mag):', [(round(fr[sel][i],2), int(sp[sel][i])) for i in top])

f0 = 53.3
tr, mr = env_at(ref, sr, f0)
tm, mm = env_at(mine, sr, f0)
# 归一化到同尺度
mm2 = mm * (np.sqrt((ref**2).mean())/np.sqrt((mine**2).mean()))
print('\n t(s)   ref_env   mine_env(norm)')
for t0 in np.arange(s, e+0.001, 0.02):
    ir = np.argmin(abs(tr-t0)); im = np.argmin(abs(tm-t0))
    print('%6.2f  %8.5f  %8.5f' % (tr[ir], mr[ir], mm2[im]))
