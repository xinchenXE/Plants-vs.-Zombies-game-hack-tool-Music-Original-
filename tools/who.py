import wave, numpy as np, os
D=r'E:\project\test\keil_keygen\FunkyStars_Original'; SR=44100
st=np.fromfile(os.path.join(D,'stems.bin'),dtype='<i2'); nf=len(st)//20
st=st[:nf*20].reshape(nf,10,2).astype(float)
W=sr=int(0.1*SR)
targets=[7.5,8.4,22.4,24.6,25.5,26.1,28.3,29.8,32.0,32.9,33.5,37.2,60.6,63.0,65.2,100.3,108.6,113.9,117.6,123.6,128.9,132.6,136.3,137.2]
# 每通道先算归一化增益
gains=[]
for c in range(10):
    w=wave.open(os.path.join(D,'solo','solo_ch%d.wav'%c),'rb')
    r=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,2).astype(float).mean(1); w.close()
    n=min(len(r),nf); a=r[:n]; b=st[:n,c,:].mean(1)
    gains.append(np.sqrt((a**2).mean())/np.sqrt((b**2).mean())+1e-9)
print('时刻   总比   各声道比值 ch0..ch9')
for t in targets:
    a=int(t*SR)
    tot_r=[];tot_m=[]
    ratios=[]
    for c in range(10):
        w=wave.open(os.path.join(D,'solo','solo_ch%d.wav'%c),'rb')
        r=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,2).astype(float).mean(1); w.close()
        e1=np.sqrt((r[a:a+W]**2).mean())
        e2=np.sqrt((st[a:a+W,c,:].mean(1)**2).mean())*gains[c]
        ratios.append(e2/(e1+1e-9) if e1>20 else float('nan'))
        tot_r.append(r[a:a+W]); tot_m.append(st[a:a+W,c,:].mean(1)*gains[c])
    tr=np.sqrt((np.sum(tot_r,0)**2).mean()); tm=np.sqrt((np.sum(tot_m,0)**2).mean())
    print('%6.1f  %.2f  '%(t,tm/(tr+1e-9))+' '.join(('  .  ' if np.isnan(x) else '%5.2f'%x) for x in ratios))
