"""把 XM 里除指定声道外的所有声道静音（音符置 0），生成 solo 文件。
用于和自家重放器的 -DSTEMS 输出逐声道比对。"""
import struct, sys, os

SRC = r'E:\project\test\keil_keygen\FunkyStars_Original\hybrid_song.xm'
OUT = r'E:\project\test\keil_keygen\FunkyStars_Original\solo'

d = bytearray(open(SRC, 'rb').read())
assert d[:17] == b'Extended Module: '
nch  = struct.unpack_from('<H', d, 68)[0]
npat = struct.unpack_from('<H', d, 70)[0]
print('channels', nch, 'patterns', npat)

# pattern 头从 60 + 头部长度 开始（本模块头部长度 276，即 336）
hdrlen = struct.unpack_from('<I', d, 60)[0]
off = 60 + hdrlen
pats = []
for i in range(npat):
    hl = struct.unpack_from('<I', d, off)[0]
    rows = struct.unpack_from('<H', d, off + 5)[0]
    dsz  = struct.unpack_from('<H', d, off + 7)[0]
    dataoff = off + hl
    pats.append((rows, dataoff, dsz))
    off = dataoff + dsz
print('pattern 表:', [(r, o, s) for r, o, s in pats])

def cell_spans(data, rows, nch):
    """返回每个 (row,ch) 单元里 note/ins 字节的位置，以及单元总长度"""
    i = 0
    spans = []
    for r in range(rows):
        for c in range(nch):
            b = data[i]
            note = ins = None
            if b & 0x80:
                j = i + 1
                if b & 1: note = j; j += 1
                if b & 2: ins  = j; j += 1
                if b & 4: j += 1
                if b & 8: j += 1
                if b & 16: j += 1
            else:
                note = i; ins = i + 1
                j = i + 5
            spans.append((note, ins))
            i = j
    return spans, i

# 预先算好每个 pattern 的单元布局
layouts = []
for rows, doff, dsz in pats:
    spans, used = cell_spans(d[doff:doff + dsz], rows, nch)
    layouts.append(spans)
    assert used == dsz, (used, dsz)

os.makedirs(OUT, exist_ok=True)
for keep in range(nch):
    m = bytearray(d)
    for pi, (rows, doff, dsz) in enumerate(pats):
        spans = layouts[pi]
        for idx, (note, ins) in enumerate(spans):
            c = idx % nch
            if c == keep:
                continue
            if note is not None: m[doff + note] = 0
            if ins  is not None: m[doff + ins]  = 0
    fn = os.path.join(OUT, 'solo_ch%d.xm' % keep)
    open(fn, 'wb').write(m)
print('生成', nch, '个 solo 文件到', OUT)
