import wave, numpy as np
REF=r'E:\project\test\keil_keygen\FunkyStars_Original\ref_openmpt.wav'
MINE=r'E:\project\test\keil_keygen\FunkyStars_Original\mine.raw'
w=wave.open(REF,'rb'); sr=w.getframerate()
r=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,2).astype(np.float64)
b=np.fromfile(MINE,dtype='<i2').reshape(-1,2).astype(np.float64)
n=min(len(r),len(b)); r=r[:n]; b=b[:n]

print('=== 左右声道独立比对 ===')
for ci,nm in ((0,'L'),(1,'R')):
    x=r[:,ci]; y=b[:,ci]
    g=np.sqrt((x**2).mean())/np.sqrt((y**2).mean())
    print('%s 声道: ref RMS %.0f  mine RMS %.0f  归一化增益 %.4f' % (nm,np.sqrt((x**2).mean()),np.sqrt((y**2).mean()),g))
    W=sr//10; M=len(x)//W
    rat=np.array([np.sqrt((y[i*W:(i+1)*W]**2).mean())/(np.sqrt((x[i*W:(i+1)*W]**2).mean())+1e-9) for i in range(M)])*g
    print('   100ms 比值 中位 %.4f  0.8~1.25 占比 %.2f%%' % (np.median(rat),100*np.mean((rat>0.8)&(rat<1.25))))

print('\n=== 声像（立体声平衡）逐秒 ===')
print(' 输入信号 = L+R，平衡 = (R-L)/(R+L)，范围 -1(全左) .. +1(全右)')
WL=sr
print('  t(s)   ref平衡  mine平衡   ref宽度  mine宽度')
def bal(x,y):
    L,R=x,y
    return (R-L)/(np.abs(L)+np.abs(R)+1e-9)
def wd(x,y):
    # 侧/中 能量比 -> 立体声宽度
    M=(x+y)/2; S=(x-y)/2
    return np.sqrt((S**2).mean())/(np.sqrt((M**2).mean())+1e-9)
for s in range(1, len(r)//WL-1):
    a=s*WL
    br=bal(r[a:a+WL,0],r[a:a+WL,1]).mean()
    bm=bal(b[a:a+WL,0],b[a:a+WL,1]).mean()
    print('  %5d  %+6.3f   %+6.3f    %5.3f    %5.3f' % (s,br,bm,wd(r[a:a+WL,0],r[a:a+WL,1]),wd(b[a:a+WL,0],b[a:a+WL,1])))
