import wave, numpy as np, os, sys
D=r'E:\project\test\keil_keygen\FunkyStars_Original'; SR=44100
st=np.fromfile(os.path.join(D,'stems.bin'),dtype='<i2'); nf=len(st)//20
st=st[:nf*20].reshape(nf,10,2).astype(float)
ch=int(sys.argv[1]); lo=float(sys.argv[2]) if len(sys.argv)>2 else 0.7
hi=float(sys.argv[3]) if len(sys.argv)>3 else 1.4
w=wave.open(os.path.join(D,'solo','solo_ch%d.wav'%ch),'rb')
ref=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,2).astype(float)
W=SR//2; K=min(len(ref),nf)//W
mm=st[:K*W,ch,:].mean(1); rr=ref[:K*W].mean(1)
e1=np.array([np.sqrt((rr[i*W:(i+1)*W]**2).mean()) for i in range(K)])
e2=np.array([np.sqrt((mm[i*W:(i+1)*W]**2).mean()) for i in range(K)])
act=e1>25
g=np.sqrt((e1[act]**2).sum()/(e2[act]**2).sum())
rat=e2*g/np.maximum(e1,1e-9)
print('ch%d 归一化增益 %.4f   全曲 RMS ref %.0f mine(norm) %.0f'%(ch,g,e1[act].mean(),(e2[act]*g).mean()))
bad=np.where(act&((rat<lo)|(rat>hi)))[0]
print('异常窗口 %d / %d'%(len(bad),act.sum()))
for i in bad:
    print('  %6.1fs  ref %7.1f  mine %7.1f  比 %.2f'%(i*0.5,e1[i],e2[i]*g,rat[i]))
