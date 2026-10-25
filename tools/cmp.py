#!/usr/bin/env python3
"""Compare the player's raw PCM render against an openmpt123 reference WAV."""
import sys, wave
import numpy as np

ref_path = sys.argv[1] if len(sys.argv) > 1 else 'ref_openmpt.wav'
mine_path = sys.argv[2] if len(sys.argv) > 2 else 'mine.raw'

w = wave.open(ref_path, 'rb')
sr = w.getframerate()
r = np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').reshape(-1, 2).astype(np.float32)
b = np.fromfile(mine_path, dtype='<i2').reshape(-1, 2).astype(np.float32)
n = min(len(r), len(b))
rr = r[:n].mean(axis=1)
bb = b[:n].mean(axis=1)
print('ref %.2fs   mine %.2fs' % (len(r) / sr, len(b) / sr))
print('峰值 mine %.0f / %.0f (32767=满)  削波样本 %d' %
      (abs(b[:, 0]).max(), abs(b[:, 1]).max(), int((np.abs(b) >= 32767).sum())))
print('整曲 RMS  ref %.1f  mine %.1f  比 %.4f' %
      (np.sqrt((rr ** 2).mean()), np.sqrt((bb ** 2).mean()), np.sqrt((bb ** 2).mean()) / np.sqrt((rr ** 2).mean())))

W = sr // 10
M = n // W
rat = np.empty(M)
er = np.empty(M)
for s in range(M):
    a = s * W
    e1 = np.sqrt((rr[a:a + W] ** 2).mean()); e2 = np.sqrt((bb[a:a + W] ** 2).mean())
    er[s] = e1; rat[s] = e2 / (e1 + 1e-9)
mask = er > 60
act = rat[mask]
print('100ms 窗口 %d: 中位 %.3f  |比-1|中位 %.4f' % (M, np.median(rat), np.median(np.abs(rat - 1))))
print('  有声窗口 %d: 中位 %.3f  0.8~1.25 占比 %.1f%%  低%d 高%d' %
      (mask.sum(), np.median(act), 100 * np.mean((act > 0.8) & (act < 1.25)),
       np.sum(act < 0.8), np.sum(act > 1.25)))
low = np.where(mask & (rat < 0.8))[0]
if len(low):
    print('  偏低时间点:', ['%.1f' % (i / 10) for i in low[:30]])
high = np.where(mask & (rat > 1.25))[0]
if len(high):
    print('  偏高时间点:', ['%.1f' % (i / 10) for i in high[:30]])

bands = [(40, 80), (80, 160), (160, 320), (320, 640), (640, 1250),
         (1250, 2500), (2500, 5000), (5000, 10000), (10000, 20000)]
Wf = sr
ds = []
for s in range(1, n // Wf - 1):
    a = s * Wf
    fr = np.abs(np.fft.rfft(rr[a:a + Wf] * np.hanning(Wf)))
    fb = np.abs(np.fft.rfft(bb[a:a + Wf] * np.hanning(Wf)))
    f = np.fft.rfftfreq(Wf, 1 / sr)
    vr = []; vb = []
    for lo, hi in bands:
        m = (f >= lo) & (f < hi)
        vr.append(np.sqrt((fr[m] ** 2).mean())); vb.append(np.sqrt((fb[m] ** 2).mean()))
    ds.append(20 * np.log10((np.array(vb) + 1) / (np.array(vr) + 1)))
ds = np.array(ds)
print('9 频段中位偏差(dB):', ' '.join('%+.2f' % v for v in np.median(ds, axis=0)))
print('逐秒整体偏差 中位 %+.2f dB   |偏差|95分位 %.2f dB' % (np.median(ds), np.percentile(np.abs(ds), 95)))
