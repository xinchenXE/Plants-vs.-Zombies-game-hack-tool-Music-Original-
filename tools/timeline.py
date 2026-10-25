import struct, sys
D=r'E:\project\test\keil_keygen\FunkyStars_Original\hybrid_song.xm'
d=open(D,'rb').read()
nch=struct.unpack_from('<H',d,68)[0]; npat=struct.unpack_from('<H',d,70)[0]
songlen=struct.unpack_from('<H',d,64)[0]; order=list(d[80:80+songlen])
hdrlen=struct.unpack_from('<I',d,60)[0]; off=60+hdrlen
pats=[]
for i in range(npat):
    rows=struct.unpack_from('<H',d,off+5)[0]; dsz=struct.unpack_from('<H',d,off+7)[0]
    pats.append((rows,off+9,dsz)); off=off+9+dsz
def cells(pi):
    rows,doff,dsz=pats[pi]; out=[];i=doff
    for r in range(rows):
        row=[]
        for c in range(nch):
            b=d[i]
            if b&0x80:
                j=i+1; n=ins=v=e=pa=0
                if b&1: n=d[j]; j+=1
                if b&2: ins=d[j]; j+=1
                if b&4: v=d[j]; j+=1
                if b&8: e=d[j]; j+=1
                if b&16: pa=d[j]; j+=1
                i=j
            else:
                n,ins,v,e,pa=d[i],d[i+1],d[i+2],d[i+3],d[i+4]; i+=5
            row.append((n,ins,v,e,pa))
        out.append(row)
    return out
NOTES='C-0 C#0 D-0 D#0 E-0 F-0 F#0 G-0 G#0 A-0 A#0 B-0'.split()
ROW=6*2.5/130.0
def nn(n):
    if n==0: return '...'
    if n==97: return 'OFF'
    return '%s%d'%(NOTES[(n-1)%12],(n-1)//12)
ch=int(sys.argv[1])
t=0.0
for oi,pi in enumerate(order):
    cl=cells(pi)
    for r,row in enumerate(cl):
        n,ins,v,e,pa=row[ch]
        if n or ins or v or e:
            print('%7.2fs  ord%2d(row%4d) pat%2d r%02d  %s ins%02d vol%02X eff%X%02X' % (t+ r*ROW,oi,oi*64+r,pi,r,nn(n),ins,v,e,pa))
    t+=len(cl)*ROW
