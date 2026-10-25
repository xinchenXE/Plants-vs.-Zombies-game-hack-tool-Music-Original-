#!/usr/bin/env python3
"""XM module structural analysis — for sizing the player's static buffers
and finding out which effects/tables the module actually needs."""
import struct, sys, collections, hashlib

path = sys.argv[1] if len(sys.argv) > 1 else 'hybrid_song.xm'
d = open(path, 'rb').read()
print('file      :', path)
print('size      :', len(d))
print('md5       :', hashlib.md5(d).hexdigest())
print('sig       :', d[:17])
print('name      :', d[17:37].rstrip(b'\x00').decode('latin1'))
print('tracker   :', d[38:58].rstrip(b'\x00').decode('latin1'))
print('version   : 0x%04x' % struct.unpack_from('<H', d, 58)[0])

o = 60
hs = struct.unpack_from('<I', d, o)[0]; o += 4
print('hdrsize   :', hs)
songlen, nrestart, nch, npat, ninst, flags, ltempo, btempo = struct.unpack_from('<8H', d, o); o += 16
print('songlen   :', songlen, ' restart:', nrestart)
print('channels  :', nch)
print('patterns  :', npat)
print('instrs    :', ninst)
print('flags     : 0x%X  (linear freq: %s)' % (flags, bool(flags & 1)))
print('tempo/bpm : %d / %d' % (ltempo, btempo))
order = list(d[o:o + 256])[:songlen]
print('order     :', order)
used_pat = sorted(set(order))
print('used pats :', used_pat, ' max=', max(order))
o += 256
if hs > 276:
    o += hs - 276

pats = []
for i in range(npat):
    ph = struct.unpack_from('<I', d, o)[0]
    sz = struct.unpack_from('<H', d, o + 7)[0]
    rows = struct.unpack_from('<H', d, o + 5)[0]
    pats.append((o, ph, sz, rows))
    o += ph + sz
print('pat rows  :', sorted(set(p[3] for p in pats)))

# ---- instruments / samples ----
print()
print('%-4s %-8s %-7s %-6s %-4s %-4s %-4s %-4s %-5s %s' %
      ('ins', 'len', 'loop', 'loopln', 'vol', 'fin', 'type', 'pan', 'rel', 'env'))
total = 0
maxend = 0
insts = []
for i in range(ninst):
    isz = struct.unpack_from('<I', d, o)[0]
    ns = struct.unpack_from('<H', d, o + 27)[0]
    shs = struct.unpack_from('<I', d, o + 29)[0]
    vn = d[o + 225]; vt = d[o + 233]
    row = []
    base = o + isz
    p = base
    lens = []
    for k in range(ns):
        ln, ls, ll = struct.unpack_from('<III', d, p)
        vol = d[p + 12]; fin = struct.unpack_from('<b', d, p + 13)[0]
        typ = d[p + 14]; pan = d[p + 15]; rel = struct.unpack_from('<b', d, p + 16)[0]
        row.append((ln, ls, ll, vol, fin, typ, pan, rel))
        lens.append(ln)
        total += ln
        e = (ls + ll) if (ll and (typ & 1)) else ln
        maxend = max(maxend, e)
        p += shs
    insts.append((i + 1, ns, row, vn, vt))
    if ns == 1:
        ln, ls, ll, vol, fin, typ, pan, rel = row[0]
        print('%-4d %-8d %-7d %-6d %-4d %-4d %-4d %-4d %-5d n=%d t=%02X' %
              (i + 1, ln, ls, ll, vol, fin, typ, pan, rel, vn, vt))
    elif ns > 1:
        print('%-4d  MULTI-SAMPLE ns=%d' % (i + 1, ns))
    else:
        print('%-4d  (empty)' % (i + 1))
    o = p + sum(lens)

print()
print('TOTAL PCM BYTES  :', total)
print('MAX SAMPLE END   :', maxend, ' (需要 g_smpBuf >= 这个数)')
print('MAX instruments  :', ninst)

# ---- envelope dump ----
print()
print('=== 音量包络 ===')
o2 = 60 + 4 + 16 + 256
if hs > 276:
    o2 += hs - 276
for i in range(npat):
    ph = struct.unpack_from('<I', d, o2)[0]; sz = struct.unpack_from('<H', d, o2 + 7)[0]
    o2 += ph + sz
for i in range(ninst):
    isz = struct.unpack_from('<I', d, o2)[0]
    ns = struct.unpack_from('<H', d, o2 + 27)[0]
    shs = struct.unpack_from('<I', d, o2 + 29)[0]
    vn = d[o2 + 225]
    vt = d[o2 + 233]
    vs, vl, vle = d[o2 + 227], d[o2 + 228], d[o2 + 229]
    fo = struct.unpack_from('<H', d, o2 + 239)[0]
    pts = [struct.unpack_from('<HH', d, o2 + 129 + j * 4) for j in range(vn)]
    if vn:
        print('ins%-3d type=%02X sust=%d loop=%d-%d fade=%d  %s' % (i + 1, vt, vs, vl, vle, fo, pts))
    base = o2 + isz
    p = base
    lens = []
    for k in range(ns):
        lens.append(struct.unpack_from('<I', d, p)[0]); p += shs
    o2 = p + sum(lens)

# ---- effects ----
print()
print('=== 效果 / 音量列 统计 ===')
eff = collections.Counter()
volcmd = collections.Counter()
notes = collections.Counter()
cells_per_ch = [0] * nch
for i, (base, ph, sz, rows) in enumerate(pats):
    p = base + ph
    end = p + sz
    for r in range(rows):
        for c in range(nch):
            b = d[p]; p += 1
            if b & 0x80:
                note = ins = vol = ef = pa = 0
                if b & 1: note = d[p]; p += 1
                if b & 2: ins = d[p]; p += 1
                if b & 4: vol = d[p]; p += 1
                if b & 8: ef = d[p]; p += 1
                if b & 16: pa = d[p]; p += 1
            else:
                note = b; ins = d[p]; vol = d[p + 1]; ef = d[p + 2]; pa = d[p + 3]; p += 4
            if ef:
                eff[(ef, pa)] += 1
            else:
                eff[(0, pa)] += 1        # 效果 0 也要按真实参数统计，否则 arpeggio 会被漏掉
            if vol:
                volcmd[vol >> 4] += 1
            if note:
                notes[note] += 1
                cells_per_ch[c] += 1
    assert p == end, (i, p, end)
for k, v in sorted(eff.items()):
    print('   eff %X%02X  x%d' % (k[0], k[1], v))
print('   音量列高 4 位:', dict(sorted(volcmd.items())))
print('   每通道音符数:', cells_per_ch, ' 总', sum(cells_per_ch))
print('   keyoff(97):', notes.get(97, 0))
