# tools/make_reel_ig.py — Owner's Math Instagram Reel (IG-only format, separate from YT/TikTok shorts).
# Rules (Instagram recommendations, Nov 2026):
#   * 1080x1920, 30 fps, 15-19 s, no watermark / no "full video on the channel" YouTube elements
#   * 0-1.5 s: ONLY the shock number on black ([NUMBER] + [FAIL]), voice starts at frame 0
#   * a cut or zoom at least every ~1.5 s (b-roll split into ~1.5 s pieces, each with a slow push-in)
#   * key numbers pop in huge, yellow #FFD60A, above the footage
#   * captions: white, bold, 2-3 words, centred; English voice and English captions
#   * last line = save CTA ("Save this...") — saves are what IG pushes
#   * voice: Kokoro, natural pacing (speed varies per line, pauses vary), own music bed (original audio)
# usage: python3 tools/make_reel_ig.py spec.json out.mp4 [cover.png]
#   spec: {"project","hook":["$48 MILLION","FROM YOUR WALK TO THE GATE"],"cover":["$48M","WALK?"],
#          "lines":[{"say","cap"?,"n"?,"find"?,"speed"?,"pause"?}]}
import json, os, re, subprocess, sys, tempfile, math, numpy as np, soundfile as sf

ROOT = '/home/claude/razgon-2d-studio'
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from make_short3 import kokoro, trim, toks, ts, esc, SR

Y = '&H0AD6FF&'  # #FFD60A in ASS (BGR)
PANEL_Y, PANEL_H = 600, 760  # footage panel 1080x760


def cover(spec, out):
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new('RGB', (1080, 1920), 'black'); d = ImageDraw.Draw(im)
    f = '/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf'
    words = spec['cover']; size = 260
    while True:
        fo = ImageFont.truetype(f, size)
        if max(d.textlength(w, font=fo) for w in words) < 980: break
        size -= 10
    hgt = size * 1.08 * len(words); y = 760 - hgt / 2
    for w in words:
        d.text((540, y), w, font=fo, fill='#FFD60A', anchor='mt'); y += size * 1.08
    hero = Image.open(os.path.join(ROOT, 'shorts_v4', 'hero1.png')).convert('RGBA')
    hero = hero.resize((int(hero.width * 1.15), int(hero.height * 1.15)))
    im.paste(hero, (1080 - hero.width - 40, 1920 - hero.height - 120), hero)
    im.save(out, quality=95)


def build(spec, out):
    proj = os.path.join(ROOT, 'projects', spec['project'])
    src = os.path.join(proj, 'out', sorted(f for f in os.listdir(os.path.join(proj, 'out')) if f.endswith('.mp4'))[0])
    sents = json.load(open(os.path.join(proj, 'timeline', 'sentences.json')))
    vdur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', src]))
    W = tempfile.mkdtemp(prefix='ig_')

    # 1) voice: per-line speed and pause vary so it doesn't sound flat
    k = kokoro(); audio = []; cur = 0.0; lines = []
    speeds = [1.12, 1.04, 1.10, 1.0, 1.08, 1.02]
    for i, ln in enumerate(spec['lines']):
        sp = ln.get('speed', speeds[i % len(speeds)])
        a, _ = k.create(ln['say'], voice=spec.get('voice', 'am_michael'), speed=sp, lang='en-us'); a = trim(a.astype(np.float32)); d = len(a) / SR
        tk = ln.get('cap', ln['say']).split(); wts = [len(re.sub(r'[^A-Za-z0-9$¢%]', '', w)) + 1.5 for w in tk]; tot = sum(wts); t = cur; words = []
        for w, wt in zip(tk, wts):
            dd = d * wt / tot; words.append((w, t, t + dd)); t += dd
        lines.append(dict(ln, start=cur, end=cur + d))
        lines[-1]['words'] = words
        gap = ln.get('pause', 0.32 if ln['say'].rstrip().endswith(('.', '?')) and i % 2 else 0.16) if i < len(spec['lines']) - 1 else 0.0
        audio += [a, np.zeros(int(gap * SR), np.float32)]; cur += d + gap
    total = cur + 0.6
    sf.write(os.path.join(W, 'vo.wav'), np.concatenate(audio + [np.zeros(int(0.6 * SR), np.float32)]), SR)
    hook_end = 1.5

    # 2) b-roll in ~1.5 s pieces after the hook, each a different matching moment, with a slow push-in
    used = []; pieces = []; t = hook_end
    for ln in lines:
        a, b = max(ln['start'], hook_end), (ln['end'] if ln is not lines[-1] else total)
        if ln is not lines[-1]:
            nxt = lines[lines.index(ln) + 1]['start']; b = nxt
        if b <= a: continue
        n = max(1, round((b - a) / 1.5))
        want = set(toks(ln.get('find', '') + ' ' + ln['say']))
        cand = sorted((s for s in sents if 1.0 < s['start'] < vdur - 30),
                      key=lambda s: -(len(want & set(toks(s['text']))) + (0.5 if ln.get('find') and ln['find'].lower() in s['text'].lower() else 0)))
        for j in range(n):
            st = next((s['start'] for s in cand if all(abs(s['start'] - u) > 4 for u in used)), 5 + 7 * len(pieces))
            used.append(st); pieces.append((st + (j % 2) * 1.6, (b - a) / n))
    parts = []
    for j, (st, d) in enumerate(pieces):
        p = os.path.join(W, f'p{j}.mp4'); parts.append(p)
        z = "1.0+0.0022*on" if j % 2 == 0 else "1.10-0.0022*on"
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{st:.3f}', '-t', f'{d:.3f}', '-i', src, '-an', '-vf',
                        f"fps=30,crop=iw:ih*0.745:0:ih*0.128,scale=1440:1015,zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x{PANEL_H}:fps=30,"
                        "curves=all='0/0 0.25/0.33 0.6/0.75 1/1',eq=saturation=1.35,setsar=1",
                        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', p], check=True)
    open(os.path.join(W, 'l.txt'), 'w').write(''.join(f"file '{p}'\n" for p in parts))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', os.path.join(W, 'l.txt'), '-c', 'copy', os.path.join(W, 'broll.mp4')], check=True)

    # 3) overlay
    ev = []
    h = spec['hook']
    ev.append(f'Dialogue: 5,{ts(0)},{ts(hook_end)},Hook,,0,0,0,,{{\\an5\\pos(540,820)\\c{Y}\\fscx92\\fscy92\\t(0,250,\\fscx100\\fscy100)}}{esc(h[0])}')
    if len(h) > 1:
        ev.append(f'Dialogue: 5,{ts(0)},{ts(hook_end)},Hook2,,0,0,0,,{{\\an5\\pos(540,1060)}}{esc(h[1])}')
    # big yellow numbers pop above the panel
    nl = [ln for ln in lines if ln.get('n') and ln['start'] >= hook_end - 0.3]
    for i, ln in enumerate(nl):
        st = max(ln['start'], hook_end); en = nl[i + 1]['start'] if i + 1 < len(nl) else total
        ev.append(f'Dialogue: 4,{ts(st)},{ts(en)},Num,,0,0,0,,{{\\an2\\pos(540,{PANEL_Y - 30})\\fscx135\\fscy135\\t(0,220,\\fscx100\\fscy100)}}{esc(ln["n"])}')
    # captions 2-3 words, white bold, centred under the panel
    caps = []
    for ln in lines[:-1] if spec.get('cta_big', True) else lines:
        c = []
        for w in ln['words']:
            c.append(w)
            if len(c) >= 3 or (len(c) >= 2 and re.search(r'[.,!?;:—]$', w[0])): caps.append([c[0][1], c[-1][2], ' '.join(x[0] for x in c)]); c = []
        if c: caps.append([c[0][1], c[-1][2], ' '.join(x[0] for x in c)])
    for i, c in enumerate(caps):
        if c[0] < hook_end: c[0] = hook_end
        if i + 1 < len(caps): c[1] = min(max(c[1], caps[i + 1][0]), caps[i + 1][0])
        if c[1] > c[0]: ev.append(f'Dialogue: 3,{ts(c[0])},{ts(c[1])},Cap,,0,0,0,,{{\\an8\\pos(540,{PANEL_Y + PANEL_H + 60})}}{esc(c[2].upper())}')
    # save CTA on the last line
    last = lines[-1]
    cta = spec.get('cta', ['SAVE THIS', "so you don't forget the numbers"])
    ev.append(f'Dialogue: 6,{ts(last["start"])},{ts(total)},CtaBox,,0,0,0,,{{\\an7\\pos(0,0)\\p1}}m 0 0 l 1080 0 l 1080 1920 l 0 1920{{\\p0}}')
    ev.append(f'Dialogue: 7,{ts(last["start"])},{ts(total)},Hook,,0,0,0,,{{\\an5\\pos(540,800)\\c{Y}\\fscx90\\fscy90\\t(0,250,\\fscx100\\fscy100)}}{esc(cta[0])}')
    ev.append(f'Dialogue: 7,{ts(last["start"])},{ts(total)},Hook2,,0,0,0,,{{\\an5\\pos(540,990)}}{esc(cta[1])}')
    ass = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hook,Inter Display,168,&H000AD6FF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,40,40,0,1
Style: Hook2,Inter Display,76,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,60,60,0,1
Style: Num,Inter Display,190,&H000AD6FF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,6,0,2,30,30,0,1
Style: Cap,Inter Display,92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,6,0,8,40,40,0,1
Style: CtaBox,Arial,20,&H00000000,&H00000000,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + '\n'.join(ev) + '\n'
    assp = os.path.join(W, 'o.ass'); open(assp, 'w').write(ass)

    # 4) compose: black canvas, footage panel after the hook, small hero, ticks on numbers
    A = os.path.join(ROOT, 'shorts_v4')
    nt = [max(ln['start'], hook_end) for ln in nl]
    t1 = nt[0] if nt else hook_end; t2 = nt[-1] if len(nt) > 1 else last['start']
    fc = (f"color=c=black:s=1080x1920:r=30:d={total:.2f}[bk];"
          f"[0:v]setpts=PTS-STARTPTS+{hook_end}/TB[fp];[bk][fp]overlay=0:{PANEL_Y}:eof_action=pass:enable='gte(t,{hook_end})'[c0];"
          "[3:v]scale=iw*0.62:-1[h1];[4:v]scale=iw*0.62:-1[h2];[5:v]scale=iw*0.62:-1[h3];"
          f"[c0][h1]overlay=x=W-w-20:y=H-h-40+8*sin(2*PI*t*1.4):enable='between(t,{hook_end},{t1:.2f})'[c1];"
          f"[c1][h2]overlay=x=W-w-20:y=H-h-40+5*sin(2*PI*t*3):enable='between(t,{t1:.2f},{t2:.2f})'[c2];"
          f"[c2][h3]overlay=x=W-w-20:y=H-h-40+10*abs(sin(2*PI*t*1.6)):enable='gte(t,{t2:.2f})'[c3];"
          f"[c3]ass={assp},fps=30,format=yuv420p[v];"
          f"[1:a]aresample=48000[vo];[2:a]aresample=48000,volume=0.13,afade=t=in:d=0.2,afade=t=out:st={total - 0.8:.2f}:d=0.8[bed];")
    inputs = ['-i', os.path.join(W, 'broll.mp4'), '-i', os.path.join(W, 'vo.wav'), '-ss', str(spec.get('bed_at', 40)), '-t', f'{total:.2f}', '-i', os.path.join(ROOT, 'audio/beds/bed_mix.wav')]
    for kk in (1, 2, 3): inputs += ['-loop', '1', '-t', f'{total:.2f}', '-i', os.path.join(A, f'hero{kk}.png')]
    sys.path.insert(0, os.path.join(ROOT, 'audio')); from sfx import tick as tkf
    tw = np.asarray(tkf(), dtype=np.float32)
    if tw.ndim == 2 and tw.shape[0] == 2: tw = tw.T
    sf.write(os.path.join(W, 'tick.wav'), tw, 48000)
    for t in nt: inputs += ['-itsoffset', f'{t:.3f}', '-i', os.path.join(W, 'tick.wav')]
    fc += ''.join(f'[{6 + i}:a]aresample=48000,volume=0.4[t{i}];' for i in range(len(nt)))
    fc += f"[vo][bed]{''.join(f'[t{i}]' for i in range(len(nt)))}amix=inputs={2 + len(nt)}:normalize=0,alimiter=limit=0.95,loudnorm=I=-14:TP=-1.5[au]"
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex', fc, '-map', '[v]', '-map', '[au]', '-t', f'{total:.2f}',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-r', '30', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', out], check=True)
    subprocess.run(['rm', '-rf', W])
    return round(total, 1)


if __name__ == '__main__':
    if sys.argv[1] == '--batch':
        specs = json.load(open(sys.argv[2])); od = sys.argv[3]
        for sp in specs:
            o = os.path.join(od, sp['name'] + '_ig.mp4')
            if os.path.exists(o) and '--force' not in sys.argv: print('skip', sp['name']); continue
            print('OK', sp['name'], build(sp, o), flush=True); cover(sp, o.replace('.mp4', '_cover.jpg'))
    else:
        sp = json.load(open(sys.argv[1])); print('OK', build(sp, sys.argv[2]))
        cover(sp, sys.argv[3] if len(sys.argv) > 3 else sys.argv[2].replace('.mp4', '_cover.jpg'))
