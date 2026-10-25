import wave, numpy as np, os
D=r'E:\project\test\keil_keygen\FunkyStars_Original'
SR=44100; NCH=10
st=np.fromfile(os.path.join(D,'stems.bin'),dtype='<i2')
nf=len(st)//(NCH*2)
st=st[:nf*NCH*2].reshape(nf,NCH,2).astype(np.float64)

W=SR//2   # 0.5 s 窗口
M=min(nf,np.load if False else nf)//W

print('声道  ref总RMS   mine总RMS  增益   ref声像  mine声像   包络相关   前3个最大偏差时刻')
summary=[]
for c in range(NCH):
    w=wave.open(os.path.join(D,'solo','solo_ch%d.wav'%c),'rb')
    ref=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,2).astype(np.float64)
    w.close()
    n=min(len(ref),nf); ref=ref[:n]; mine=st[:n,c,:]
    rr=ref.mean(1); mm=mine.mean(1)
    er=np.sqrt((rr**2).mean()); em=np.sqrt((mm**2).mean())
    if er<50:
        print('ch%d  参考几乎静音 (RMS %.0f)'%(c,er)); continue
    g=er/em if em>1 else 0
    # 声像
    pr=ref[:,1].mean()/ (ref[:,0].mean()+ref[:,1].mean()+1e-9) if abs(ref.mean())>1 else 0
    panr=np.abs(ref[:,1]).sum()/(np.abs(ref[:,0]).sum()+np.abs(ref[:,1]).sum()+1e-9)
    panm=np.abs(mine[:,1]).sum()/(np.abs(mine[:,0]).sum()+np.abs(mine[:,1]).sum()+1e-9)
    # 包络相关 + 逐窗比值
    K=n//W
    e1=np.array([np.sqrt((rr[i*W:(i+1)*W]**2).mean()) for i in range(K)])
    e2=np.array([np.sqrt((mm[i*W:(i+1)*W]**2).mean())*g for i in range(K)])
    act=e1>30
    if act.sum()>2:
        cor=np.corrcoef(e1[act],e2[act])[0,1]
        rat=e2[act]/(e1[act]+1e-9) if False else e2[act]/np.maximum(e1[act],1e-9)
    else:
        cor=float('nan'); rat=np.array([1.0])
    bad=np.where(act)[0][np.argsort(np.abs(np.log(np.maximum(rat,1e-9))))[::-1][:3]]
    print('ch%d  %8.0f  %8.0f  %6.3f  %6.3f  %6.3f   %8.3f   %s' % (
        c,er,em,g,panr,panm,cor,' '.join('%.1fs(%.2f)'%(i*W/SR,rat[np.where(np.where(act)[0]==i)[0][0]]) for i in bad)))
    summary.append((c,er,panr,panm,cor))
