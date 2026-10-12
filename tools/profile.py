# LIGHTS ON: builds every SVG on the profile. Standard library only, so the daily GitHub Action can run it.
#   python3 tools/profile.py            all art (stats from the API with GH_TOKEN/GITHUB_TOKEN, or the `gh` CLI)
#   python3 tools/profile.py --daily    the same, plus (inside GitHub Actions) the wolf-hunt ledger from issues
# One glowing route runs down the page at x=96; every section is a station on it; it ends at 10 NOV.
import base64, datetime as dt, hashlib, json, math, os, pathlib, random, re, subprocess, sys, urllib.request
from xml.sax.saxutils import escape as esc

ROOT = pathlib.Path(__file__).resolve().parent.parent
A = ROOT / 'assets'
ICONS = ROOT / 'src' / 'icons'
USER = 'thearchitect0x-glitch'
REPO = f'{USER}/{USER}'
BETA = dt.date(2026, 11, 10)
TODAY = dt.date.fromisoformat(os.environ.get('PROFILE_DAY', dt.date.today().isoformat()))
DAYS = (BETA - TODAY).days


def seeded(tag, day=TODAY):
    return random.Random(int(hashlib.sha256(f'{day.isoformat()}:{tag}'.encode()).hexdigest(), 16))


MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
SANS = "'Helvetica Neue',Helvetica,Arial,sans-serif"
BG, PANEL, INK = '#05040a', '#0c0a16', '#1f4fd8'
GOLD, GREEN, PINK, CYAN, ORANGE, VIOLET, YELLOW, RED = '#F7CD45', '#39ff88', '#ff2bd6', '#00e5ff', '#ff7a1a', '#7a5cff', '#fff23a', '#ff3b5c'
ACID = [PINK, VIOLET, CYAN, GREEN, YELLOW, ORANGE, PINK]
RAIL_X = 96
W = 1280

# ---------------------------------------------------------------- the wolf hunt: one mini wolf, one slot, one word a day
WORDS = ['EMMENTAL', 'GRUYERE', 'COMTE', 'RACLETTE', 'GOUDA', 'HAVARTI', 'MANCHEGO', 'BRIE', 'APPENZELLER', 'TILSIT',
         'JARLSBERG', 'FONTINA', 'TALEGGIO', 'REBLOCHON', 'EDAM', 'CHEDDAR', 'PECORINO', 'GORGONZOLA', 'MIMOLETTE', 'BEAUFORT']
SLOTS = {  # slot: poses that make sense there (never peek or handstand: they need a partner prop)
    'div1': ['strut', 'toss', 'lookback', 'back'], 'div2': ['strut', 'toss', 'lookback', 'back'], 'div3': ['strut', 'toss', 'lookback', 'back'],
    'board': ['loaf', 'loaf-cheese'], 'timeline': ['cheesehat', 'lookback'], 'wall': ['loaf'], 'stats': ['loaf-cheese', 'loaf'],
    'rules': ['cheesehat'], 'footer': ['strut', 'loaf'],
}


def word_for(day):
    return seeded('word', day).choice(WORDS)


_h = seeded('hunt')
HUNT = {'slot': _h.choice(sorted(SLOTS)), 'word': word_for(TODAY)}
HUNT['pose'] = _h.choice(SLOTS[HUNT['slot']])
if 0 < DAYS <= 7 and 'cheesehat' in SLOTS[HUNT['slot']]: HUNT['pose'] = 'cheesehat'


def uri(path, mime=None):
    p = pathlib.Path(path)
    mime = mime or {'.jpg': 'image/jpeg', '.png': 'image/png', '.svg': 'image/svg+xml', '.webp': 'image/webp'}[p.suffix]
    return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"


_CAST = {}


def cast(name):
    if name not in _CAST: _CAST[name] = uri(A / 'cast' / f'{name}.webp')
    return _CAST[name]


META = json.loads((A / 'cast' / 'meta.json').read_text())


def uid(*k):
    return hashlib.md5(repr(k).encode()).hexdigest()[:8]


def hexrgb(c):
    return tuple(int(c[i:i + 2], 16) / 255 for i in (1, 3, 5))


LAST_IMG = [None]


def ground(name, cx, floor, height, key='#ffffff', side=1, flip=False, night=True, shadow=1.0, rim=.38):
    """A cut-out that BELONGS in the scene: ambient occlusion, a contact shadow the feet touch, a rim of the scene's
    key light on the light side, the figure graded toward that light. Feet land exactly on `floor`, centred at `cx`.
    Returns (svg, box) where box = (x, y, w, h); draw an occluder after it to finish the job."""
    m = META[name]
    s = height / m['foot']
    w, h = m['w'] * s, m['h'] * s
    fc = (m['fx0'] + m['fx1']) / 2 * s
    x = cx - (w - fc if flip else fc); y = floor - m['foot'] * s
    span = max(24, (m['fx1'] - m['fx0']) * s)
    k = uid(name, cx, floor, height, key, side, flip, night)
    r, g, b = hexrgb(key)
    dim = .9 if night else 1.0
    tf = f' transform="translate({2 * x + w:.1f} 0) scale(-1 1)"' if flip else ''
    defs = (f'<filter id="rim{k}" x="-10%" y="-10%" width="120%" height="120%"><feFlood flood-color="{key}"/><feComposite in2="SourceAlpha" operator="in"/>'
            f'<feOffset dx="{2 * side * (-1 if flip else 1)}" dy="-1.5"/><feGaussianBlur stdDeviation="1.2"/></filter>'
            f'<filter id="gr{k}" color-interpolation-filters="sRGB"><feComponentTransfer>'
            f'<feFuncR type="linear" slope="{dim * .9:.3f}" intercept="{.10 * r * dim:.3f}"/><feFuncG type="linear" slope="{dim * .9:.3f}" intercept="{.10 * g * dim:.3f}"/>'
            f'<feFuncB type="linear" slope="{dim * .9:.3f}" intercept="{.10 * b * dim:.3f}"/></feComponentTransfer></filter>'
            f'<filter id="ao{k}" x="-60%" y="-300%" width="220%" height="700%"><feGaussianBlur stdDeviation="12"/></filter>'
            f'<filter id="cs{k}" x="-60%" y="-300%" width="220%" height="700%"><feGaussianBlur stdDeviation="2.5"/></filter>')
    img = cast(name)
    out = (f'<defs>{defs}</defs>'
           f'<ellipse cx="{cx:.1f}" cy="{floor:.1f}" rx="{span * .85:.1f}" ry="{max(6, span * .14):.1f}" fill="#000" opacity="{.38 * shadow:.2f}" filter="url(#ao{k})"/>'
           f'<ellipse cx="{cx:.1f}" cy="{floor - 1:.1f}" rx="{span * .55:.1f}" ry="{max(3, span * .05):.1f}" fill="#000" opacity="{.7 * shadow:.2f}" filter="url(#cs{k})"/>'
           f'<use href="#im{k}" filter="url(#rim{k})" opacity="{rim}"/>'
           f'<use href="#im{k}" filter="url(#gr{k})"/>')
    out = out.replace('<defs>', f'<defs><image id="im{k}" href="{img}" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"{tf}/>', 1)
    LAST_IMG[0] = f'im{k}'
    return out, (x, y, w, h)


def text(x, y, s, size=16, col='#fff', op=1, font=MONO, weight=400, anchor='start', ls=0, extra=''):
    return (f'<text x="{x:.1f}" y="{y:.1f}" fill="{col}" fill-opacity="{op}" font-family="{font}" font-size="{size}" font-weight="{weight}" '
            f'text-anchor="{anchor}" letter-spacing="{ls}" {extra}>{esc(s)}</text>')


def pill(x, y, s, bg=YELLOW, fg=BG, size=15, anchor='start'):
    w = 26 + len(s) * size * .6
    x0 = x - w / 2 if anchor == 'middle' else (x - w if anchor == 'end' else x)
    return (f'<rect x="{x0:.1f}" y="{y - size - 8:.1f}" width="{w:.1f}" height="{size + 16}" rx="{(size + 16) / 2}" fill="{bg}"/>'
            + text(x0 + w / 2, y + 1, s, size, fg, anchor='middle', weight=700))


def cheese(x, y, s=1.0, word=None):
    """A wedge of Swiss cheese, drawn (no emoji in SVG)."""
    p = f'M{x:.1f},{y:.1f} l{30 * s:.1f},{-12 * s:.1f} l{8 * s:.1f},{18 * s:.1f} l{-38 * s:.1f},{6 * s:.1f}z'
    holes = ''.join(f'<circle cx="{x + dx * s:.1f}" cy="{y + dy * s:.1f}" r="{r * s:.1f}" fill="#b07a00" opacity=".55"/>' for dx, dy, r in ((12, -2, 2.6), (24, 2, 2), (31, -5, 1.6)))
    w = text(x + 19 * s, y + 3 * s, word, 6.5 * s, '#5a3d00', .8, weight=700, anchor='middle') if word else ''
    return f'<path d="{p}" fill="{YELLOW}" stroke="#c99a00" stroke-width="{.8 * s:.1f}"/>{holes}{w}'


def mini(slot, cx, floor, key=YELLOW, night=True):
    """Today's mini wolf, if today's slot is this one: ~50 px, grounded, the word of the day on his cheese."""
    if HUNT['slot'] != slot: return ''
    g, (x, y, w, h) = ground('wolf-' + HUNT['pose'], cx, floor, 50, key, 1, night=night, shadow=.8)
    return g + cheese(x + w + 2, floor - 3, .62, HUNT['word'])


GLOW = ('<filter id="glow" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="5" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        '<filter id="soft" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="18"/></filter>'
        '<filter id="hue"><feColorMatrix type="hueRotate" values="0"><animate attributeName="values" values="0;360" dur="16s" repeatCount="indefinite"/></feColorMatrix></filter>')


def svg(w, h, body, label, defs='', comment=''):
    c = f'<!-- {comment} -->' if comment else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{esc(label)}">{c}'
            f'<defs>{GLOW}{defs}</defs>{body}</svg>')


def card_bg(h, rx=22, col='#fff', op=.10):
    return (f'<rect width="{W}" height="{h}" rx="{rx}" fill="{BG}"/>'
            f'<rect x="1" y="1" width="{W - 2}" height="{h - 2}" rx="{rx}" fill="none" stroke="{col}" stroke-opacity="{op}"/>')


def rail(h, top, bot, y0=0, y1=None, light=False):
    """The route: enters at the top, leaves at the bottom, tunnel-mouth ticks so the gaps between images read as stations."""
    y1 = h if y1 is None else y1
    k = uid('rail', h, top, bot, y0, y1, light)
    a, b = (INK, INK) if light else (top, bot)
    ticks = ''.join(f'<line x1="{RAIL_X - 11}" y1="{yy}" x2="{RAIL_X + 11}" y2="{yy}" stroke="{c}" stroke-width="2" opacity=".7"/>'
                    for yy, c in ((y0 + 1, a), (y1 - 1, b)) if yy in (1, h - 1))
    return (f'<defs><linearGradient id="rl{k}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient></defs>'
            f'<line x1="{RAIL_X}" y1="{y0}" x2="{RAIL_X}" y2="{y1}" stroke="url(#rl{k})" stroke-width="6" opacity=".9"/>{ticks}'
            f'<circle r="5" fill="#fff" filter="url(#glow)"><animateMotion path="M{RAIL_X},{y0} L{RAIL_X},{y1}" dur="{max(1.2, (y1 - y0) / 160):.1f}s" repeatCount="indefinite"/></circle>')


def roundel(y, col, label):
    return (f'<circle cx="{RAIL_X}" cy="{y}" r="24" fill="{BG}" stroke="{col}" stroke-width="5"/>'
            f'<circle cx="{RAIL_X}" cy="{y}" r="24" fill="none" stroke="{col}" stroke-width="2"><animate attributeName="r" values="24;40" dur="2.4s" repeatCount="indefinite"/><animate attributeName="opacity" values=".8;0" dur="2.4s" repeatCount="indefinite"/></circle>'
            + text(RAIL_X, y + 6, label, 16, col, font=SANS, weight=900, anchor='middle'))


def cycle(attr, off=0, dur=9):
    vals = ACID[off:] + ACID[1:off + 1] if off else ACID
    return f'<animate attributeName="{attr}" values="{";".join(vals)}" dur="{dur}s" repeatCount="indefinite"/>'


def deimos(cx, cy, s, color='#fff', node='#fff'):
    R = 154 * s
    v = [(cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))) for a in (-90, 150, 30)]
    tri = ' '.join(f'{x:.1f},{y:.1f}' for x, y in v)
    spokes = ''.join(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}"/>' for x, y in v)
    nodes = ''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{19 * s:.1f}"/>' for x, y in v)
    return (f'<g fill="none" stroke="{color}" stroke-linejoin="round"><circle cx="{cx}" cy="{cy}" r="{R:.1f}" stroke-width="{8 * s:.1f}" stroke-opacity=".8"/>'
            f'<polygon points="{tri}" stroke-width="{7 * s:.1f}"/><g stroke-width="{6 * s:.1f}">{spokes}</g></g>'
            f'<g fill="{node}">{nodes}<circle cx="{cx}" cy="{cy}" r="{26.5 * s:.1f}"/></g>')


def stars(w, h, n, rng):
    return ''.join(f'<circle cx="{rng.randint(0, w)}" cy="{rng.randint(0, h)}" r="{rng.choice((.7, 1, 1.4))}" fill="#fff">'
                   f'<animate attributeName="opacity" values=".1;.8;.1" dur="{rng.uniform(2, 6):.1f}s" begin="{rng.uniform(0, 4):.1f}s" repeatCount="indefinite"/></circle>'
                   for _ in range(n))


def gear(gx, gy, r, teeth, dur, col='#fff', rev=False):
    pts = ' '.join(f'{gx + (r if i % 4 in (0, 1) else r * .82) * math.cos(2 * math.pi * i / (teeth * 4)):.1f},'
                   f'{gy + (r if i % 4 in (0, 1) else r * .82) * math.sin(2 * math.pi * i / (teeth * 4)):.1f}' for i in range(teeth * 4))
    return (f'<g><polygon points="{pts}" fill="none" stroke="{col}" stroke-width="2.2"/><circle cx="{gx}" cy="{gy}" r="{r * .35:.1f}" fill="none" stroke="{col}" stroke-width="2"/>'
            f'<animateTransform attributeName="transform" type="rotate" from="0 {gx} {gy}" to="{"-360" if rev else "360"} {gx} {gy}" dur="{dur}s" repeatCount="indefinite"/></g>')


# ================================================================ S1 HERO: the map lights up (dark: night map; light: blueprint)
STATIONS = [('CLOCKFORD', GOLD, (110, 86), 'end'), ('RATCHET', GREEN, (510, 66), 'start'), ('CRIMP', PINK, (548, 250), 'end'), ('MARKLODE', CYAN, (490, 420), 'end'), ('M.A.X', ORANGE, (168, 430), 'end')]


def hero(light=False):
    rng = random.Random(11)
    H, cx, cy, floor = 540, 310, 245, 512
    fg = INK if light else '#fff'
    k = 'L' if light else 'D'
    defs = (f'<filter id="blur{k}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="55"/></filter>'
            f'<radialGradient id="pet{k}"><stop offset="0" stop-color="#fff">{cycle("stop-color", 2, 7)}</stop><stop offset="1" stop-color="{PINK}">{cycle("stop-color", 4, 7)}</stop></radialGradient>'
            f'<radialGradient id="pet2{k}"><stop offset="0" stop-color="{CYAN}">{cycle("stop-color", 3, 5)}</stop><stop offset="1" stop-color="{VIOLET}" stop-opacity=".2">{cycle("stop-color", 5, 5)}</stop></radialGradient>'
            f'<linearGradient id="tg{k}" x1="0" x2="1"><stop offset="0" stop-color="{YELLOW}">{cycle("stop-color", 1, 6)}</stop><stop offset=".5" stop-color="#fff"/><stop offset="1" stop-color="{CYAN}">{cycle("stop-color", 4, 6)}</stop></linearGradient>'
            f'<clipPath id="type{k}"><rect x="610" y="300" width="0" height="30"><animate attributeName="width" values="0;560;560;560;0" keyTimes="0;.25;.4;.9;1" dur="11s" repeatCount="indefinite"/></rect></clipPath>'
            f'<clipPath id="type2{k}"><rect x="610" y="331" width="0" height="30"><animate attributeName="width" values="0;0;330;330;0" keyTimes="0;.28;.42;.9;1" dur="11s" repeatCount="indefinite"/></rect></clipPath>'
            f'<clipPath id="card{k}"><rect width="{W}" height="{H}" rx="22"/></clipPath>'
            f'<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".22"/></pattern>'
            f'<pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="{INK}" stroke-opacity=".10"/></pattern>')

    def mandala(n, r0, r1, wd, dur, rev, grad):
        petal = f'M0,{-r0} C{wd},{-(r0 + r1) / 2} {wd},{-(r0 + r1) / 2 - 10} 0,{-r1} C{-wd},{-(r0 + r1) / 2 - 10} {-wd},{-(r0 + r1) / 2} 0,{-r0}Z'
        ps = ''.join(f'<path d="{petal}" transform="rotate({360 * i / n})"/>' for i in range(n))
        return (f'<g transform="translate({cx} {cy})"><g fill="{"none" if light else "url(#" + grad + ")"}" fill-opacity=".55" stroke="{fg}" stroke-opacity="{.32 if light else .18}">{ps}'
                f'<animateTransform attributeName="transform" type="rotate" from="0" to="{-360 if rev else 360}" dur="{dur}s" repeatCount="indefinite"/></g></g>')

    routes = ''
    for i, (name, col, (sx, sy), anc) in enumerate(STATIONS):
        t0 = .4 + i * .5
        L = math.hypot(sx - cx, sy - cy) + 40
        mx, my = (cx + sx) / 2 + (sy - cy) * .18, (cy + sy) / 2 - (sx - cx) * .18
        c = INK if light else col
        left = anc == 'end'
        lx = sx - 14 if left else sx + 14
        hl = (f'<rect x="{(lx - len(name) * 8.2 - 4) if left else lx - 4:.0f}" y="{sy - 28}" width="{len(name) * 8.2 + 8:.0f}" height="15" fill="{col}" opacity=".45"/>' if light else '')
        routes += (f'<path d="M{cx},{cy} Q{mx:.0f},{my:.0f} {sx},{sy}" fill="none" stroke="{c}" stroke-width="3" stroke-dasharray="{L:.0f}" stroke-dashoffset="{L:.0f}" stroke-linecap="round">'
                   f'<animate attributeName="stroke-dashoffset" values="{L:.0f};{L:.0f};0;0" keyTimes="0;{t0 / 14:.3f};{(t0 + .5) / 14:.3f};1" dur="14s" repeatCount="indefinite"/></path>'
                   f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1" keyTimes="0;{(t0 + .5) / 14:.3f};{(t0 + .6) / 14:.3f};1" dur="14s" repeatCount="indefinite"/>{hl}'
                   f'<circle cx="{sx}" cy="{sy}" r="9" fill="{col}" stroke="{fg}" stroke-width="2"/>'
                   + text(lx, sy - 16, name, 12, c, anchor='end' if left else 'start', weight=700, ls=2) + '</g>')
    L6 = 560
    routes += (f'<path d="M{cx},{cy} C{cx - 70},{cy + 140} {RAIL_X},{cy + 120} {RAIL_X},{H}" fill="none" stroke="{fg}" stroke-width="6" stroke-dasharray="{L6}" stroke-dashoffset="{L6}">'
               f'<animate attributeName="stroke-dashoffset" values="{L6};{L6};0;0" keyTimes="0;.21;.3;1" dur="14s" repeatCount="indefinite"/></path>')
    ticks = ''.join(f'<line x1="{cx}" y1="{cy - 222}" x2="{cx}" y2="{cy - (204 if i % 5 else 194)}" transform="rotate({i * 6} {cx} {cy})"/>' for i in range(60))
    title = 'THE ARCHITECT'
    glitch = lambda col, xs: (f'<text x="610" y="210" fill="{col}" opacity=".85" font-family="{SANS}" font-size="66" font-weight="900" letter-spacing="3">{title}'
                              f'<animate attributeName="x" values="{xs}" dur="2.6s" calcMode="discrete" repeatCount="indefinite"/></text>')
    wg, (wx, wy, ww, wh) = ground('wolf-strut', 0, floor, 150, '#ffe9c2' if light else PINK, 1, night=not light)
    say = 'bright in here. good thing i brought shades.' if light else '3 a.m.? good. you’re one of us.'
    if 0 < DAYS <= 7: say = f'{DAYS} days. bring cheese.'
    walk = (f'<g><animateTransform attributeName="transform" type="translate" values="-200 0;-200 0;{RAIL_X + 1010} 0;{RAIL_X + 1010} 0;{W + 220} 0" keyTimes="0;.14;.43;.86;1" dur="14s" repeatCount="indefinite"/>'
            f'{wg}<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;.55;.57;.84;.86;1" dur="14s" repeatCount="indefinite"/>'
            + pill(-30, wy - 14, say, INK if light else YELLOW, '#fff' if light else BG, 15, 'middle') + '</g></g>')
    ledge = (f'<rect x="0" y="{floor}" width="{W}" height="{H - floor}" fill="{"#eef2ff" if light else "#0a0812"}"/>'
             f'<line x1="0" y1="{floor + .5}" x2="{W}" y2="{floor + .5}" stroke="{fg}" stroke-opacity=".25"/>')
    if light:
        engine = (f'<rect width="{W}" height="{H}" fill="#fff"/><rect width="{W}" height="{H}" fill="url(#grid)"/>'
                  f'{mandala(12, 40, 190, 46, 48, False, "pet" + k)}{mandala(24, 120, 236, 22, 70, True, "pet2" + k)}'
                  f'<g stroke="{INK}" stroke-opacity=".5" stroke-width="2">{ticks}<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="60s" repeatCount="indefinite"/></g>'
                  f'{gear(1225, 60, 26, 10, 8, INK)}')
        headline = f'<text x="610" y="210" fill="{INK}" font-family="{SANS}" font-size="66" font-weight="900" letter-spacing="3">{title}</text>'
    else:
        blobs = ''
        for i, (x, y, r) in enumerate([(160, 120, 210), (420, 340, 230), (760, 110, 200), (1080, 330, 240), (620, 420, 180)]):
            dx, dy = rng.randint(-90, 90), rng.randint(-60, 60)
            blobs += (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{ACID[i]}">{cycle("fill", i + 1, 11 + i * 2)}'
                      f'<animateTransform attributeName="transform" type="translate" values="0 0;{dx} {dy};0 0" dur="{13 + i * 3}s" repeatCount="indefinite"/></circle>')
        engine = (f'<rect width="{W}" height="{H}" fill="{BG}"/><g filter="url(#hue)"><g filter="url(#blur{k})" opacity=".42">{blobs}</g>'
                  f'{mandala(12, 40, 190, 46, 48, False, "pet" + k)}{mandala(24, 120, 236, 22, 70, True, "pet2" + k)}'
                  f'<g stroke="#fff" stroke-opacity=".7" stroke-width="2">{ticks}<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="60s" repeatCount="indefinite"/></g>'
                  f'{gear(1225, 60, 26, 10, 8)}</g>')
        headline = (glitch(CYAN, "607;610;613;606;610;610;611") + glitch(PINK, "613;610;607;614;610;610;609")
                    + f'<text x="610" y="210" fill="url(#tg{k})" font-family="{SANS}" font-size="66" font-weight="900" letter-spacing="3">{title}</text>')
    tc = INK if light else GREEN
    body = (f'<g clip-path="url(#card{k})">{engine}{routes}<g filter="url(#glow)">{deimos(cx, cy, .62, fg, fg)}</g>'
            f'{headline}{text(614, 256, "CO-FOUNDER · DEIMOS AI LLC", 21, fg, .85, ls=3)}'
            f'<g clip-path="url(#type{k})">{text(614, 322, "> I see the whole system. Lit up like a map.", 19, tc)}</g>'
            f'<g clip-path="url(#type2{k})">{text(614, 352, "> Then I build the answer.", 19, tc)}</g>'
            f'<rect x="614" y="362" width="11" height="18" fill="{tc}"><animate attributeName="opacity" values="1;0" dur=".8s" calcMode="discrete" repeatCount="indefinite"/></rect>'
            f'{text(614, 420, "ARCHITECT · ENGINEER · SYSTEMS THINKER", 14, fg, .7, ls=4)}'
            f'{ledge}'
            f'<rect x="0" y="{floor - 1}" width="{W}" height="4" fill="{"#dfe6ff" if light else "#120f20"}"/>'
            + rail(H, '#fff', GOLD, floor, H, light) + ('' if light else f'<rect width="{W}" height="{H}" fill="url(#scan)"/>') + '</g>'
            f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="none" stroke="{fg}" stroke-opacity=".14"/>')
    comment = '' if light else f'you read the source. he respects that. today’s word: {HUNT["word"]}'
    return svg(W, H, body, 'The Architect, co-founder of Deimos AI LLC: a glowing map with five routes from the Deimos mark to Clockford, Ratchet, Crimp, Marklode and M.A.X.', defs, comment)


# ================================================================ S3 THE BOARD
def board():
    sunday = TODAY.weekday() == 6
    beta = f'PRIVATE BETA IN {DAYS} DAYS' if DAYS > 1 else ('PRIVATE BETA TOMORROW' if DAYS == 1 else 'PRIVATE BETA IS OPEN')
    rows = [('CLOCKFORD', GOLD, beta, 'patent pending'), ('RATCHET', GREEN, 'LIVE · 1,000 EFFECTS / MONTH FREE', 'ratchetgate.com'),
            ('CRIMP', PINK, 'OPEN SOURCE · PATENT PENDING', 'github'), ('MARKLODE', CYAN, 'TAKING IDEAS · 24–72 H', 'marklode.com'),
            ('M.A.X', ORANGE, 'OFFLINE-FIRST · IN THE LAB', 'deimoscore.com')]
    if sunday: rows.append(('THE WOLF', YELLOW, 'ON DUTY · CHEESE RESERVES: CLASSIFIED', 'sundays only'))
    top, X0 = 150, 150
    H = top + 70 + len(rows) * 42 + 20
    body = card_bg(H) + rail(H, GOLD, GOLD)
    body += f'<rect x="{X0 - 20}" y="{top}" width="{W - X0 - 20}" height="{H - top - 20}" rx="14" fill="{PANEL}" stroke="{GOLD}" stroke-opacity=".25"/>'
    wg, (wx, wy, ww, wh) = ground('wolf-cheesehat', X0 + 110, top + 1, 124, GOLD, -1)
    body += wg + f'<rect x="{X0 - 20}" y="{top - 2}" width="{W - X0 - 20}" height="6" rx="2" fill="#1d1929"/>'   # the frame lip in front of his paws
    if DAYS > 0: body += pill(wx + ww + 16, wy + 44, 'reporting for beta.', GOLD, BG, 14)
    body += text(X0 + 420, 70, 'NOW', 14, op=.55, ls=6) + text(W - 50, 70, f'BOARD UPDATED {TODAY.strftime("%d %b %Y").upper()}', 12, op=.4, anchor='end', ls=3)
    for i, (name, col, status, where) in enumerate(rows):
        y = top + 56 + i * 42
        t = .3 + i * .35
        cells = ''.join(f'<rect x="{X0 + 28 + c * 22}" y="{y - 22}" width="19" height="30" rx="3" fill="#15121f"/>' for c in range(10))
        body += (f'<circle cx="{X0 + 6}" cy="{y - 7}" r="6" fill="{col}"><animate attributeName="opacity" values="1;.25;1" dur="{1.6 + i * .3:.1f}s" repeatCount="indefinite"/></circle>{cells}'
                 + ''.join(f'<text x="{X0 + 38 + c * 22}" y="{y}" text-anchor="middle" fill="{col}" font-family="{MONO}" font-size="19" font-weight="700" opacity="0">{esc(ch)}'
                           f'<animate attributeName="opacity" values="0;1" begin="{t + c * .05:.2f}s" dur=".01s" fill="freeze"/></text>' for c, ch in enumerate(name))
                 + f'<clipPath id="st{i}"><rect x="{X0 + 270}" y="{y - 24}" height="32" width="0"><animate attributeName="width" from="0" to="700" begin="{t + .5:.2f}s" dur=".9s" fill="freeze"/></rect></clipPath>'
                 + f'<g clip-path="url(#st{i})">{text(X0 + 270, y, status, 18, "#fff", .92, ls=2)}</g>' + text(W - 60, y, where, 13, col, .7, anchor='end', ls=1))
    body += mini('board', W - 240, H - 26, GOLD)
    return svg(W, H, body, f'Now: Clockford {beta.lower()}; Ratchet live with 1,000 effects a month free; Crimp open source; Marklode taking ideas; M.A.X in the lab.')


# ================================================================ S4 THE STATIONS (five linked bands; the last two smaller)
def band(h, col, letter, head, lines, tags, art, note=None):
    body = card_bg(h, col=col, op=.18) + rail(h, col, col) + roundel(70, col, letter)
    body += f'<circle cx="980" cy="{h / 2}" r="190" fill="{col}" opacity=".07" filter="url(#soft)"/>'
    body += text(150, 82, head, 34, col, font=SANS, weight=900, ls=.5)
    body += ''.join(text(152, 118 + i * 25, l, 16, op=.88) for i, l in enumerate(lines))
    if note: body += text(152, 118 + len(lines) * 25 + 4, note, 12.5, op=.55, extra='font-style="italic"')
    x = 152
    for t in tags:
        w = 18 + len(t) * 8.4
        body += f'<rect x="{x}" y="{h - 52}" width="{w:.0f}" height="28" rx="14" fill="none" stroke="{col}" stroke-opacity=".6"/>' + text(x + w / 2, h - 33, t, 11, col, anchor='middle', ls=1.5)
        x += w + 10
    return body + art


def st_clockford():
    h, col, floor = 300, GOLD, 282
    rg, _ = ground('rook', 880, floor, 236, CYAN, -1)
    px, py, pw, ph = 990, 64, 150, 216
    cards = [('agent · send invoice', 'APPROVE', GREEN), ('agent · ship deploy', 'APPROVE', GREEN), ('agent · move $9,400', 'STOP', RED)]
    cyc, stack = 9, ''
    for i, (what, verdict, vc) in enumerate(cards):
        a, b = i / 3, (i + 1) / 3
        last = i == 2
        ym = py + 70
        stack += (f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;{1 if last else 0};0" keyTimes="0;{a:.3f};{a + .02:.3f};{b - .02:.3f};{b - .001:.3f};1" dur="{cyc}s" repeatCount="indefinite"/>'
                  f'<animateTransform attributeName="transform" type="translate" values="0 80;0 80;0 0;0 0" keyTimes="0;{a:.3f};{a + .06:.3f};1" dur="{cyc}s" repeatCount="indefinite"/>'
                  f'<rect x="{px + 12}" y="{ym}" width="{pw - 24}" height="74" rx="10" fill="#15121f" stroke="#fff" stroke-opacity=".15"/>'
                  + text(px + 22, ym + 24, what, 10.5, op=.85)
                  + f'<rect x="{px + 22}" y="{ym + 38}" width="{pw - 44}" height="26" rx="13" fill="{vc}" opacity=".2"><animate attributeName="opacity" values=".2;.2;1;1" keyTimes="0;{a + .14:.3f};{a + .16:.3f};1" dur="{cyc}s" repeatCount="indefinite"/></rect>'
                  + text(px + pw / 2, ym + 56, verdict, 12, '#fff' if last else BG, weight=900, anchor='middle', ls=3) + '</g>')
    phone = (f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="22" fill="#0b0912" stroke="#fff" stroke-opacity=".5" stroke-width="3"/>'
             f'<rect x="{px + pw / 2 - 22}" y="{py + 10}" width="44" height="8" rx="4" fill="#fff" opacity=".2"/>'
             + text(px + pw / 2, py + 46, 'CLOCKFORD', 10, GOLD, weight=700, anchor='middle', ls=3) + stack
             + f'<rect x="{px - 6}" y="{floor - 7}" width="{pw + 12}" height="9" rx="3" fill="#1d1929"/>')
    art = (f'<ellipse cx="960" cy="{floor + 4}" rx="200" ry="10" fill="{CYAN}" opacity=".08"/>' + rg + phone
           + f'<line x1="760" y1="{floor + .5}" x2="{W - 30}" y2="{floor + .5}" stroke="#fff" stroke-opacity=".1"/>')
    body = band(h, col, 'C', 'Your agents. Your phone. Your call.', ['See, approve and stop your AI agents from your', 'phone, whichever company built them.'],
                ['CLOCKFORD', 'PATENT PENDING', 'PRIVATE BETA 10 NOV'], art)
    return svg(W, h, body, 'Clockford: see, approve and stop your AI agents from your phone, whichever company built them. Patent pending, private beta 10 November.')


def st_ratchet():
    h, col, floor = 270, GREEN, 248
    cyc = 9
    toss = ''
    for i in range(3):
        a = i / 3
        toss += (f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{a:.3f};{a + .01:.3f};{a + .3:.3f};{a + .31:.3f};1" dur="{cyc}s" repeatCount="indefinite"/>'
                 + pill(880, 120 + i * 40, f'retry {i + 1}', '#15121f', GREEN, 13, 'middle') + '</g>')
    wg = ''
    x0, y0 = 990, 150
    printer = (f'<rect x="{x0}" y="{y0}" width="170" height="{floor - y0}" rx="12" fill="#14121c" stroke="{GREEN}" stroke-opacity=".5"/>'
               f'<rect x="{x0 + 30}" y="{y0 - 4}" width="110" height="8" rx="3" fill="#000"/>'
               f'<rect x="{x0 + 136}" y="{y0 + 20}" width="14" height="8" rx="2" fill="{GREEN}"><animate attributeName="opacity" values="1;.2;1" dur="1.2s" repeatCount="indefinite"/></rect>'
               + text(x0 + 85, y0 + 60, 'EFFECTS', 10, GREEN, .7, anchor='middle', ls=3) + text(x0 + 85, y0 + 84, '1', 22, GREEN, weight=900, anchor='middle')
               + f'<clipPath id="paper"><rect x="{x0 + 30}" y="{y0 - 112}" width="110" height="110"/></clipPath><g clip-path="url(#paper)">'
               f'<g><animateTransform attributeName="transform" type="translate" values="0 106;0 106;0 0;0 0" keyTimes="0;.1;.2;1" dur="{cyc}s" repeatCount="indefinite"/>'
               f'<rect x="{x0 + 36}" y="{y0 - 106}" width="98" height="106" fill="#f4f1e8"/>'
               + text(x0 + 85, y0 - 80, 'RECEIPT', 10, '#333', weight=700, anchor='middle', ls=2)
               + f'<line x1="{x0 + 46}" y1="{y0 - 68}" x2="{x0 + 124}" y2="{y0 - 68}" stroke="#999" stroke-dasharray="3 3"/>'
               + text(x0 + 85, y0 - 42, 'CHARGED ×1', 13, '#0a6b33', weight=900, anchor='middle')
               + text(x0 + 85, y0 - 22, 'retries: 3 · effects: 1', 8.5, '#555', anchor='middle') + '</g></g>')
    art = toss + printer + f'<line x1="700" y1="{floor + .5}" x2="{W - 30}" y2="{floor + .5}" stroke="#fff" stroke-opacity=".1"/>'
    body = band(h, col, 'R', 'Retry all you want. It happens once.', ['The effect gate for AI agents: a retried charge,', 'deploy or email happens at most once.'],
                ['RATCHET', 'OPENSSF SILVER', '1,000 EFFECTS / MONTH FREE'], art)
    return svg(W, h, body, 'Ratchet: the effect gate for AI agents. A retried charge, deploy or email happens at most once.')


def st_crimp():
    h, col, cyc = 270, PINK, 8
    x0, y0 = 880, 82
    cards = ''
    for i, f in enumerate(['FACT  ·  coverage on file', 'FACT  ·  criteria met', 'FACT  ·  record complete']):
        y = y0 + i * 46
        crack = i == 1
        anim = lambda attr, a, b: f'<animate attributeName="{attr}" values="{a};{a};{b};{b};{a}" keyTimes="0;.5;.52;.95;1" dur="{cyc}s" repeatCount="indefinite"/>'
        cards += (f'<rect x="{x0}" y="{y}" width="250" height="38" rx="8" fill="#15121f" stroke="#fff" stroke-opacity=".2">{anim("fill", "#15121f", "#2a2730") if crack else ""}</rect>'
                  f'<text x="{x0 + 14}" y="{y + 24}" fill="#fff" fill-opacity=".85" font-family="{MONO}" font-size="12">{esc(f)}{anim("fill-opacity", ".85", ".3") if crack else ""}</text>'
                  + (f'<polyline points="{x0 + 120},{y} {x0 + 112},{y + 14} {x0 + 126},{y + 22} {x0 + 116},{y + 38}" fill="none" stroke="{PINK}" stroke-width="2.5" opacity="0">{anim("opacity", "0", "1")}</polyline>' if crack else ''))
    stamp = (f'<g transform="rotate(-10 1005 52)"><g>'
             f'<rect x="935" y="28" width="140" height="44" rx="6" fill="{PINK}" fill-opacity=".12" stroke="{PINK}" stroke-width="4"><animate attributeName="fill-opacity" values=".12;.12;0;0;.12" keyTimes="0;.55;.6;.95;1" dur="{cyc}s" repeatCount="indefinite"/></rect>'
             f'<g>{text(1005, 58, "DECIDED", 18, PINK, weight=900, anchor="middle", ls=4)}<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;.55;.58;.95;1" dur="{cyc}s" repeatCount="indefinite"/></g>'
             f'<g opacity="0">{text(1005, 58, "WITHDRAWN", 17, PINK, weight=900, anchor="middle", ls=3)}<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;.58;.62;.95;1" dur="{cyc}s" repeatCount="indefinite"/></g>'
             f'<animateTransform attributeName="transform" type="translate" values="0 0;0 0;0 -18;0 -18;0 0" keyTimes="0;.55;.6;.95;1" dur="{cyc}s" repeatCount="indefinite"/></g></g>')
    body = band(h, col, 'C', 'Show the facts, or it doesn’t stand.', ['Agents submit the rule and the facts, not a conclusion.', 'When a fact breaks, the decision withdraws itself.'],
                ['CRIMP', 'OPEN SOURCE', 'PATENT PENDING', 'OPENSSF SILVER'], cards + stamp,
                note='In 2022, 83% of appealed Medicare Advantage prior-auth denials were overturned.')
    return svg(W, h, body, 'Crimp, open source: agents submit the rule and facts, not a conclusion; the decision withdraws itself when a fact breaks.')


def st_marklode():
    h, col, floor, cyc = 230, CYAN, 212, 8
    dx, dy, dw, dh = 920, 44, 280, floor - 44
    tabs = ['COMPETITORS', 'PATENTS', '3 ATTACKS', 'VERDICT']
    tg = ''
    for i, t in enumerate(tabs):
        tx = dx + 6 + i * 68
        a = i / 5
        tg += (f'<rect x="{tx}" y="{dy - 18}" width="64" height="22" rx="5" fill="#15202a" stroke="{CYAN}" stroke-opacity=".5">'
               f'<animate attributeName="fill" values="#15202a;#15202a;{CYAN};#15202a;#15202a" keyTimes="0;{a:.2f};{a + .03:.2f};{a + .18:.2f};1" dur="{cyc}s" repeatCount="indefinite"/></rect>'
               + text(tx + 32, dy - 3, t, 7.5, '#fff', .9, anchor='middle', weight=700))
    dossier = (f'<rect x="{dx}" y="{dy}" width="{dw}" height="{dh}" rx="10" fill="#101820" stroke="{CYAN}" stroke-opacity=".35"/>'
               + ''.join(f'<rect x="{dx + 20}" y="{dy + 22 + j * 18}" width="{dw - 40 - (j * 41) % 90}" height="7" rx="3" fill="#fff" opacity=".14"/>' for j in range(7)) + tg
               + f'<g opacity="0" transform="rotate(-8 {dx + 190} {dy + 110})"><animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;.8;.81;.97;1" dur="{cyc}s" repeatCount="indefinite"/>'
               f'<animateTransform attributeName="transform" type="translate" additive="sum" values="0 0;0 0;2 1;-2 0;0 0" keyTimes="0;.81;.83;.85;1" dur="{cyc}s" repeatCount="indefinite"/>'
               f'<rect x="{dx + 128}" y="{dy + 90}" width="124" height="38" rx="5" fill="none" stroke="{CYAN}" stroke-width="4"/>{text(dx + 190, dy + 116, "VERDICT", 17, CYAN, weight=900, anchor="middle", ls=3)}</g>')
    art = (dossier + pill(dx - 20, floor - 12, 'read your deck. got notes.', CYAN, BG, 13, 'end')
           + f'<line x1="700" y1="{floor + .5}" x2="{W - 30}" y2="{floor + .5}" stroke="#fff" stroke-opacity=".1"/>')
    body = band(h, col, 'M', 'Get torn apart before the pitch.', ['Startup diligence in 24–72 h: competitors, overlapping', 'patents, the three strongest attacks, a verdict.'],
                ['MARKLODE', '24–72 H', 'MARKLODE.COM/SAMPLE'], art)
    return svg(W, h, body, 'Marklode: startup diligence in 24 to 72 hours: competitors, overlapping patents, the three strongest attacks, a verdict.')


def st_max():
    h, col = 210, ORANGE
    x0, y = 820, 112

    def wave(seed, spike):
        r = random.Random(seed)
        return 'M' + ' L'.join(f'{x0 + i * 10:.0f},{y + r.uniform(-9, 9) + (-50 if spike and i in (27, 28) else 0):.0f}' for i in range(41))
    vals = ';'.join(wave(s, s % 3 == 2) for s in range(6)) + ';' + wave(0, False)
    art = (f'<rect x="{x0 - 4}" y="{y - 18}" width="408" height="36" rx="8" fill="{col}" fill-opacity=".10"/>' + text(x0, y - 28, 'OWN BASELINE', 11, col, .75, ls=3)
           + f'<path d="{wave(0, False)}" fill="none" stroke="#fff" stroke-width="2.5" stroke-linejoin="round"><animate attributeName="d" values="{vals}" dur="6s" repeatCount="indefinite"/></path>'
           f'<circle cx="{x0 + 275}" cy="{y - 50}" r="12" fill="none" stroke="{col}" stroke-width="3" opacity="0"><animate attributeName="opacity" values="0;0;1;0;0;1;0" keyTimes="0;.33;.36;.5;.83;.86;1" dur="6s" repeatCount="indefinite"/></circle>')
    body = band(h, col, 'X', 'Measured against you. Not everyone.', ['Offline-first behavioral analysis for litigation', 'teams, read against each person’s own baseline.'],
                ['M.A.X', 'OFFLINE-FIRST', 'FOR LITIGATION TEAMS'], art)
    return svg(W, h, body, 'M.A.X: offline-first behavioral analysis for litigation teams, against each person’s own baseline.')


# ================================================================ S5 THE FOUR RULES
def rules():
    H, floor = 470, 392
    body = card_bg(H) + rail(H, '#fff', '#fff') + text(150, 52, 'FOUR RULES', 13, op=.5, ls=6)
    body += f'<rect x="130" y="{floor}" width="{W - 160}" height="44" fill="#0a0812"/><line x1="130" y1="{floor + .5}" x2="{W - 30}" y2="{floor + .5}" stroke="#fff" stroke-opacity=".18"/>'
    xs = [130, 412, 694, 976, 1250]
    pillars = ''.join(f'<rect x="{x - 9}" y="70" width="18" height="{floor - 70}" fill="#16131f" stroke="#fff" stroke-opacity=".08"/>' for x in xs[1:4])
    caps = [('People stay in charge', 'of what matters.'), ('Assume something', 'is already inside.'), ('If it matters,', 'make it provable.'), ('Bend,', 'don’t break.')]
    cols = [GOLD, PINK, CYAN, GREEN]
    # 1 · Rook, crossing guard: agents wait at the line until a person says go
    rg, _ = ground('rook', 225, floor, 176, '#ffffff', 1)
    oct_ = ' '.join(f'{318 + 32 * math.cos(math.radians(22.5 + 45 * i)):.1f},{floor - 178 + 32 * math.sin(math.radians(22.5 + 45 * i)):.1f}' for i in range(8))
    sign = (f'<line x1="318" y1="{floor}" x2="318" y2="{floor - 150}" stroke="#bbb" stroke-width="5"/><polygon points="{oct_}" fill="{RED}" stroke="#fff" stroke-width="3"/>'
            + text(318, floor - 172, 'STOP', 14, '#fff', weight=900, anchor='middle', ls=1))
    cars = ''.join(f'<g><rect x="{344 + i * 20}" y="{floor - 20}" width="16" height="12" rx="3" fill="{c}"/><circle cx="{348 + i * 20}" cy="{floor - 6}" r="3" fill="#000"/><circle cx="{356 + i * 20}" cy="{floor - 6}" r="3" fill="#000"/>'
                   f'<animateTransform attributeName="transform" type="translate" values="0 0;-2 0;0 0" dur="{1.5 + i * .3:.1f}s" repeatCount="indefinite"/></g>' for i, c in enumerate([CYAN, VIOLET, GREEN]))
    # 2 · the wolf has been here the whole time: his flat edge sits on the pillar's face, he ducks back in now and then
    px = xs[2] - 9
    wg, (wx, wy, ww, wh) = ground('wolf-peek', 0, floor, 156, PINK, -1, shadow=.7)
    shift = px - (wx + ww)
    p2 = (f'<clipPath id="peekclip"><rect x="{xs[1] + 10}" y="40" width="{px - xs[1] - 10}" height="{floor + 40}"/></clipPath>'
          f'<g clip-path="url(#peekclip)"><g transform="translate({shift:.1f} 0)"><g>{wg}<animateTransform attributeName="transform" type="translate" values="0 0;0 0;40 0;40 0;0 0" keyTimes="0;.7;.74;.9;1" dur="10s" repeatCount="indefinite"/></g></g></g>'
          + text((xs[1] + px) / 2, 92, 'he’s been here the whole time.', 12, PINK, .85, anchor='middle', extra='font-style="italic"'))
    # 3 · a seal pressed into a page: PROVEN
    sx, sy = 835, floor - 120
    p3 = (f'<rect x="{sx - 80}" y="{sy - 110}" width="160" height="200" rx="6" fill="#efeadd"/>'
          + ''.join(f'<rect x="{sx - 62}" y="{sy - 90 + j * 16}" width="{124 - (j * 29) % 50}" height="6" rx="3" fill="#c9c1ad"/>' for j in range(6))
          + f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1" keyTimes="0;.3;.32;1" dur="4s" repeatCount="indefinite"/>'
          f'<circle cx="{sx}" cy="{sy + 40}" r="34" fill="#b3122e"/><circle cx="{sx}" cy="{sy + 40}" r="26" fill="none" stroke="#7d0b1f" stroke-width="3"/>'
          + text(sx, sy + 45, 'PROVEN', 11, '#ffd9df', weight=900, anchor='middle', ls=1) + '</g>'
          f'<g><rect x="{sx - 14}" y="{sy - 40}" width="28" height="60" rx="6" fill="#d8c9a8"/><circle cx="{sx}" cy="{sy + 24}" r="18" fill="#a68b5b"/>'
          f'<animateTransform attributeName="transform" type="translate" values="0 -70;0 -70;0 0;0 0;0 -70" keyTimes="0;.18;.3;.45;1" dur="4s" repeatCount="indefinite"/></g>'
          f'<rect x="{sx - 84}" y="{floor - 4}" width="168" height="6" rx="2" fill="#1a1626"/>')
    # 4 · the plank bends under the handstand and springs back
    a, b = 1010, 1220
    yb = floor - 70

    def plank(sag):
        return f'M{a},{yb} Q{(a + b) / 2},{yb + sag} {b},{yb} L{b},{yb + 10} Q{(a + b) / 2},{yb + 10 + sag} {a},{yb + 10} Z'
    posts = ''.join(f'<rect x="{x - 8}" y="{yb + 6}" width="16" height="{floor - yb - 6}" fill="#2a2433"/>' for x in (a + 10, b - 10))
    hg, _ = ground('wolf-handstand', (a + b) / 2, yb + 2, 150, GREEN, 1, shadow=.6)
    spl = 'calcMode="spline" keySplines=".4 0 .6 1;.4 0 .6 1;.4 0 .6 1"'
    p4 = (posts + f'<path d="{plank(0)}" fill="#8a6a43" stroke="#5d452a"><animate attributeName="d" values="{plank(0)};{plank(14)};{plank(-3)};{plank(0)}" keyTimes="0;.35;.6;1" dur="3s" repeatCount="indefinite" {spl}/></path>'
          f'<g>{hg}<animateTransform attributeName="transform" type="translate" values="0 0;0 14;0 -3;0 0" keyTimes="0;.35;.6;1" dur="3s" repeatCount="indefinite" {spl}/></g>')
    capsv = ''.join(text((xs[i] + xs[i + 1]) / 2, floor + 22, l1, 15, c, font=SANS, weight=900, anchor='middle') + text((xs[i] + xs[i + 1]) / 2, floor + 40, l2, 15, c, font=SANS, weight=900, anchor='middle')
                    for i, ((l1, l2), c) in enumerate(zip(caps, cols)))
    body += rg + sign + cars + p3 + p4 + pillars + p2 + capsv
    if HUNT['slot'] == 'rules': body += mini('rules', xs[3], 70, GREEN)
    return svg(W, H, body, 'Four rules: people stay in charge of what matters; assume something is already inside; if it matters, make it provable; bend, don’t break.')


# ================================================================ S6 HOW I SEE IT (over the wolf's shoulder)
def how():
    rng = random.Random(3)
    H, cyc = 540, 12
    nodes = [(rng.uniform(190, 800), rng.uniform(50, 400)) for _ in range(58)]
    edges = set()
    for i, (x, y) in enumerate(nodes):
        for j in sorted(range(len(nodes)), key=lambda j: (nodes[j][0] - x) ** 2 + (nodes[j][1] - y) ** 2)[1:3]:
            edges.add(tuple(sorted((i, j))))
    edges = sorted(edges)
    weak = set(rng.sample(range(len(edges)), 6))
    g = ''
    for k, (i, j) in enumerate(edges):
        (x1, y1), (x2, y2) = nodes[i], nodes[j]
        t = .5 + k * 4.0 / len(edges)
        L = math.hypot(x2 - x1, y2 - y1)
        c = RED if k in weak else CYAN
        g += (f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{c}" stroke-width="{2.4 if k in weak else 1.4}" stroke-dasharray="{L:.0f}" stroke-dashoffset="{L:.0f}">'
              f'<animate attributeName="stroke-dashoffset" values="{L:.0f};{L:.0f};0;0;{L:.0f}" keyTimes="0;{t / cyc:.3f};{(t + .4) / cyc:.3f};.95;1" dur="{cyc}s" repeatCount="indefinite"/>'
              + (f'<animate attributeName="stroke" values="{RED};{RED};{GREEN};{GREEN}" keyTimes="0;.66;.68;1" dur="{cyc}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="stroke-opacity" values="1;.2;1;.2;1;1" keyTimes="0;.48;.52;.56;.6;1" dur="{cyc}s" repeatCount="indefinite"/>' if k in weak else '') + '</line>')
    for k, (x, y) in enumerate(nodes):
        t = k * 2.5 / len(nodes)
        g += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="4.5" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;{t / cyc:.3f};{(t + .2) / cyc:.3f};.95;1" dur="{cyc}s" repeatCount="indefinite"/></circle>'
    defs = f'<radialGradient id="mapglow" cx=".5" cy=".45" r=".6"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".35"/><stop offset=".6" stop-color="{PINK}" stop-opacity=".08"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></radialGradient><clipPath id="howc"><rect width="{W}" height="{H}" rx="22"/></clipPath>'
    wg, _ = ground('wolf-back', 270, H + 70, 330, PINK, 1, shadow=0, rim=.7)
    copy = ['Where you see a problem,', 'I see the map.']
    sub = ['Every connection. Every place it could break.', 'I sit with the hunch until the pattern clicks.', 'Then I attack my own idea harder', 'than anyone else will.']
    right = (text(860, 120, 'HOW I SEE IT', 13, op=.5, ls=6) + ''.join(text(860, 172 + i * 42, l, 34, '#fff', font=SANS, weight=900) for i, l in enumerate(copy))
             + ''.join(text(862, 272 + i * 28, l, 16, op=.85) for i, l in enumerate(sub)))
    body = (card_bg(H) + f'<g clip-path="url(#howc)"><ellipse cx="500" cy="230" rx="430" ry="260" fill="url(#mapglow)"/>' + g + wg + '</g>' + right + rail(H, '#fff', CYAN))
    return svg(W, H, body, 'How I see it: the whole system laid out like a map, every place it could break.', defs)


# ================================================================ S7 LIVE STATS (the wolf eats the graph; it grows back)
Q = '''query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{contributionCount date}}}}
repositories(ownerAffiliations:OWNER,isFork:false,first:100,privacy:PUBLIC){totalCount nodes{languages(first:10,orderBy:{field:SIZE,direction:DESC}){edges{size node{name color}}}}}}}'''


def gh_api(query, variables):
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if token:
        req = urllib.request.Request('https://api.github.com/graphql', json.dumps({'query': query, 'variables': variables}).encode(),
                                     {'Authorization': f'bearer {token}', 'Content-Type': 'application/json'})
        return json.load(urllib.request.urlopen(req, timeout=30))
    args = ['gh', 'api', 'graphql', '-f', f'query={query}'] + [a for k, v in variables.items() for a in ('-F', f'{k}={v}')]
    return json.loads(subprocess.run(args, capture_output=True, text=True, timeout=60).stdout)


def stats():
    try:
        u = gh_api(Q, {'login': USER})['data']['user']
    except Exception as e:
        print('stats: unavailable', e); return None
    cal = u['contributionsCollection']['contributionCalendar']
    weeks = cal['weeks'][-52:]
    days = [d for w in weeks for d in w['contributionDays']]
    best = max(days, key=lambda d: d['contributionCount'])
    streak = run = 0
    for d in days:
        run = run + 1 if d['contributionCount'] else 0; streak = max(streak, run)
    active = sum(1 for d in days if d['contributionCount'])
    langs = {}
    for r in u['repositories']['nodes']:
        for e in r['languages']['edges']:
            langs.setdefault(e['node']['name'], [0, e['node']['color'] or '#888'])[0] += e['size']
    tot = sum(v[0] for v in langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1][0])[:6]
    H = 400
    body = card_bg(H) + rail(H, CYAN, GREEN)
    nums = [(f"{cal['totalContributions']:,}", 'CONTRIBUTIONS, LAST YEAR', GREEN), (str(best['contributionCount']), f"BEST DAY · {dt.date.fromisoformat(best['date']).strftime('%d %b').upper()}", CYAN),
            (f'{streak} days', 'LONGEST STREAK', YELLOW), (str(active), 'DAYS SHIPPED', PINK)]
    for i, (v, l, c) in enumerate(nums):
        y = 76 + i * 76
        body += text(150, y + 6, v, 38, c, font=SANS, weight=900) + text(152, y + 30, l, 11, op=.5, ls=3)
    gx, gy, cs = 400, 54, 14
    mx = max([d['contributionCount'] for d in days] + [1])
    pal = ['#15121f', '#0f3d2a', '#167a4a', '#22b866', GREEN]
    run_s = 12.0
    hunt_cell = seeded('stats-cell').randrange(len(weeks) * 7) if HUNT['slot'] == 'stats' else None
    n = 0
    for wi, w in enumerate(weeks):
        for d in w['contributionDays']:
            di = (dt.date.fromisoformat(d['date']).weekday() + 1) % 7
            c = d['contributionCount']
            lvl = 0 if c == 0 else 1 + min(3, int(3.999 * c / mx))
            x, y = gx + wi * (cs + 2), gy + di * (cs + 2)
            k1 = (run_s * wi / len(weeks)) / run_s
            k2 = min(.999, k1 + .012)
            if n == hunt_cell:
                body += f'<path d="M{x},{y + cs} l{cs},0 l-{cs / 2:.0f},-{cs}z" fill="{YELLOW}"/>'
            elif lvl:
                body += (f'<rect x="{x}" y="{y}" width="{cs}" height="{cs}" rx="3" fill="{pal[lvl]}">'
                         f'<animate attributeName="fill" values="{pal[lvl]};{pal[lvl]};{YELLOW};{YELLOW};{pal[lvl]}" keyTimes="0;{k1:.3f};{k2:.3f};.96;1" dur="{run_s}s" repeatCount="indefinite"/></rect>'
                         f'<circle cx="{x + cs / 2}" cy="{y + cs / 2}" r="3" fill="#6b4a00" opacity="0"><animate attributeName="opacity" values="0;0;.9;.9;0" keyTimes="0;{k1:.3f};{k2:.3f};.96;1" dur="{run_s}s" repeatCount="indefinite"/></circle>')
            else:
                body += f'<rect x="{x}" y="{y}" width="{cs}" height="{cs}" rx="3" fill="{pal[0]}"/>'
            n += 1
    gw = len(weeks) * (cs + 2)
    floor = gy + 7 * (cs + 2) + 22
    body += f'<line x1="{gx - 10}" y1="{floor + .5}" x2="{gx + gw + 10}" y2="{floor + .5}" stroke="#fff" stroke-opacity=".12"/>'
    wg, _ = ground('wolf-strut', gx - 20, floor, 74, GREEN, 1)
    body += f'<g>{wg}<animateTransform attributeName="transform" type="translate" values="0 0;{gw} 0;{gw} 0" keyTimes="0;.96;1" dur="{run_s}s" repeatCount="indefinite"/></g>'
    body += text(gx, floor + 30, 'the wolf eats a year of commits every 12 seconds. it grows back.', 12, op=.5)
    by = 318
    body += text(gx, by - 12, 'LANGUAGES ACROSS PUBLIC REPOS', 11, op=.5, ls=3)
    x, tsum = gx, sum(v[0] for _, v in top) or 1
    for name, (size, col) in top:
        w = (W - 50 - gx) * size / tsum
        body += f'<rect x="{x:.1f}" y="{by}" width="{max(w - 2, 1):.1f}" height="12" rx="3" fill="{col}"/>'; x += w
    x = gx
    for name, (size, col) in top:
        lab = f'{name} {100 * size / tot:.0f}%'
        body += f'<circle cx="{x + 5}" cy="{by + 36}" r="5" fill="{col}"/>' + text(x + 16, by + 41, lab, 12, op=.8); x += 30 + len(lab) * 7.6
    body += text(W - 40, H - 16, f'live · updated {TODAY.strftime("%d %b %Y")}', 11, op=.3, anchor='end', ls=2)
    return svg(W, H, body, f"Live stats: {cal['totalContributions']} contributions in the last year; best day {best['contributionCount']}; longest streak {streak} days.")


# ================================================================ TERMINAL (kept: the owner likes it)
TERM = [('$ whoami', GREEN), ('the architect · co-founder, Deimos AI LLC', '#fff'),
        ('$ deimos ls --built', GREEN), ('clockford  (patent pending)   ratchet   crimp  (patent pending)   marklode   m.a.x', '#fff'),
        ('$ deimos badges', GREEN), ('OpenSSF Best Practices: SILVER × 2   ·   clockford private beta: 10 NOV', YELLOW),
        ('$ sleep 8h', GREEN), ('sleep: refused. the agents never sleep either.', PINK),
        ('$ wolf --where', GREEN), ('somewhere on this page. find him. read the word on his cheese.', CYAN)]


def terminal():
    Wt, H = 1000, 400
    rows, t = '', 0.4
    for i, (s, col) in enumerate(TERM):
        y = 82 + i * 30
        typing = s.startswith('$')
        d = 0.05 * len(s) if typing else 0.05
        rows += (f'<clipPath id="c{i}"><rect x="28" y="{y - 22}" height="30" width="0"><animate attributeName="width" from="0" to="{Wt}" begin="{t:.2f}s" dur="{d:.2f}s" fill="freeze"/></rect></clipPath>'
                 + text(34, y, s, 17, col, extra=f'clip-path="url(#c{i})" xml:space="preserve"'))
        t += d + (0.25 if typing else 0.7)
    cy = 82 + len(TERM) * 30
    body = (f'<rect width="{Wt}" height="{H}" rx="16" fill="#0b0a12" stroke="#fff" stroke-opacity=".12"/>'
            f'<rect width="{Wt}" height="40" rx="16" fill="#16141f"/><rect y="24" width="{Wt}" height="16" fill="#16141f"/>'
            '<circle cx="26" cy="20" r="7" fill="#ff5f57"/><circle cx="50" cy="20" r="7" fill="#febc2e"/><circle cx="74" cy="20" r="7" fill="#28c840"/>'
            + text(Wt / 2, 25, 'architect@deimos: ~', 13, op=.5, anchor='middle') + rows
            + f'<rect x="34" y="{cy - 17}" width="10" height="20" fill="{GREEN}" opacity="0"><animate attributeName="opacity" values="1;0" dur=".9s" begin="{t:.1f}s" calcMode="discrete" repeatCount="indefinite"/></rect>')
    return svg(Wt, H, body, 'A terminal: whoami, the five builds, the badges, and a refusal to sleep.')


# ================================================================ S8 THE CAST (Rook counts down on his own chest)
def cast_scene():
    rng = random.Random(9)
    H, floor = 560, 488
    rook_h, rcx, wcx = 400, 430, 830
    rg, (rx, ry, rw, rh) = ground('rook', rcx, floor, rook_h, CYAN, 1)
    rook_id = LAST_IMG[0]
    s = rook_h / META['rook']['foot']
    q = META['rook']['screen']                                        # the chest screen, measured in the cut-out (tools/meta.py)
    sx, sy, sw, sh = rx + q[0] * s, ry + q[1] * s, q[2] * s, q[3] * s
    big = str(DAYS) if DAYS > 0 else 'OPEN'
    screen = (f'<clipPath id="scr"><rect x="{sx:.1f}" y="{sy:.1f}" width="{sw:.1f}" height="{sh:.1f}" rx="4"/></clipPath>'
              f'<g clip-path="url(#scr)"><rect x="{sx:.1f}" y="{sy:.1f}" width="{sw:.1f}" height="{sh:.1f}" fill="#04121a"/>'
              + text(sx + sw / 2, sy + sh * .62, big, sh * (.6 if DAYS > 0 else .42), CYAN, weight=900, anchor='middle', extra='filter="url(#glow)"')
              + text(sx + sw / 2, sy + sh * .88, 'DAYS TO BETA' if DAYS > 0 else 'BETA', sh * .12, CYAN, .8, anchor='middle', ls=2)
              + f'<rect x="{sx:.1f}" y="{sy:.1f}" width="{sw:.1f}" height="{sh:.1f}" fill="url(#scan2)"/>'
              f'<rect x="{sx:.1f}" y="{sy:.1f}" width="{sw:.1f}" height="3" fill="{CYAN}" opacity=".25"><animate attributeName="y" values="{sy:.1f};{sy + sh:.1f}" dur="2.4s" repeatCount="indefinite"/></rect></g>'
              f'<ellipse cx="{sx + sw / 2:.1f}" cy="{floor + 6}" rx="120" ry="12" fill="{CYAN}" opacity=".10"/>')
    wg, (wx, wy, ww, wh) = ground('wolf-loaf-cheese', wcx, floor, 150, YELLOW, -1, flip=True)
    wolf_id = LAST_IMG[0]
    lines = [('rook', 'Every agent in town, accounted for.'), ('wolf', '…and every crumb of cheese.'), ('rook', 'Beta opens 10 November.'), ('wolf', 'bring cheese.')]
    bub, cyc = '', 16
    for i, (who, s_) in enumerate(lines):
        bw = 30 + len(s_) * 10.2
        bx = rx + rw * .62 if who == 'rook' else wx + ww * .5 - bw / 2
        by = ry + 10 if who == 'rook' else wy - 74
        a, b = i / 4, (i + 1) / 4
        col = '#ffffff' if who == 'rook' else YELLOW
        tail = (f'<path d="M{bx + 30},{by + 44} l-4,22 l22,-22z" fill="{col}"/>' if who == 'rook' else f'<path d="M{bx + bw / 2 - 8},{by + 44} l8,20 l8,-20z" fill="{col}"/>')
        bub += (f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{a:.3f};{a + .02:.3f};{b - .03:.3f};{b - .01:.3f};1" dur="{cyc}s" repeatCount="indefinite"/>'
                f'<rect x="{bx:.0f}" y="{by:.0f}" width="{bw:.0f}" height="46" rx="23" fill="{col}"/>{tail}' + text(bx + bw / 2, by + 30, s_, 17, BG, anchor='middle', weight=700) + '</g>')
    defs = (f'<radialGradient id="spot1" cx=".5" cy="0" r="1"><stop offset="0" stop-color="{CYAN}" stop-opacity=".30"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>'
            f'<radialGradient id="spot2" cx=".5" cy="0" r="1"><stop offset="0" stop-color="{YELLOW}" stop-opacity=".22"/><stop offset="1" stop-color="{YELLOW}" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".22"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<mask id="refl"><rect x="0" y="{floor}" width="{W}" height="70" fill="url(#fade)"/></mask>'
            f'<pattern id="scan2" width="3" height="3" patternUnits="userSpaceOnUse"><rect width="3" height="1" fill="#000" opacity=".35"/></pattern>'
            f'<clipPath id="stage"><rect width="{W}" height="{H}" rx="22"/></clipPath>')
    refl = (f'<g mask="url(#refl)" opacity=".4"><g transform="translate(0 {2 * floor}) scale(1 -1)">'
            f'<use href="#{rook_id}"/><use href="#{wolf_id}"/></g></g>')
    beam = lambda c, top, base, grad: f'<polygon points="{c - top},0 {c + top},0 {c + base},{floor} {c - base},{floor}" fill="url(#{grad})"/>'
    body = (f'<g clip-path="url(#stage)"><rect width="{W}" height="{H}" fill="{BG}"/>{stars(W, H, 60, rng)}' + beam(rcx, 60, 230, 'spot1') + beam(wcx, 50, 190, 'spot2')
            + f'<rect x="0" y="{floor}" width="{W}" height="{H - floor}" fill="#0a0812"/><line x1="0" y1="{floor}" x2="{W}" y2="{floor}" stroke="#fff" stroke-opacity=".12"/>'
            f'{refl}{rg}{screen}{wg}{bub}' + text(150, 60, 'THE CAST', 13, op=.5, ls=6)
            + text(rcx, floor + 40, 'ROOK · lives in Clockford', 13, CYAN, .85, anchor='middle', ls=2)
            + text(wcx, floor + 40, 'THE WOLF · head of security (self-appointed)', 13, YELLOW, .85, anchor='middle', ls=2)
            + rail(H, CYAN, YELLOW) + '</g>' + f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="none" stroke="#fff" stroke-opacity=".1"/>')
    return svg(W, H, body, 'Rook, the robot rabbit who lives in Clockford, counting down to the beta on his chest screen, and the wolf, head of security (self-appointed).', defs)


# ================================================================ S9 THE ROAD SO FAR (the line turns and becomes the timeline)
def timeline():
    H = 270
    pts = [('2022', 'CO-PRODUCER', 'Gaming Wall St · HBO Max', '#fff'), ('2026', 'OPENSSF SILVER × 2', 'Ratchet + Crimp', GREEN),
           ('2026', 'PATENTS PENDING', 'Clockford + Crimp', GOLD), ('10 NOV 2026', 'PRIVATE BETA', 'Clockford opens its doors', PINK)]
    x0, x1, y = 220, 1110, 140
    body = card_bg(H)
    body += f'<path d="M{RAIL_X},0 L{RAIL_X},{y - 24} Q{RAIL_X},{y} {RAIL_X + 24},{y} L{x1},{y} L{W - 76},{y} Q{W - 52},{y} {W - 52},{y + 24} L{W - 52},{H}" fill="none" stroke="#fff" stroke-width="6" opacity=".8"/>'
    body += f'<line x1="{x1 - 230}" y1="{y}" x2="{x1}" y2="{y}" stroke="{PINK}" stroke-width="6" stroke-dasharray="10 8"/>'
    body += f'<circle r="5" fill="#fff" filter="url(#glow)"><animateMotion path="M{RAIL_X},0 L{RAIL_X},{y} L{W - 52},{y} L{W - 52},{H}" dur="8s" repeatCount="indefinite"/></circle>'
    body += text(150, 50, 'THE ROAD SO FAR', 13, op=.5, ls=6)
    for i, (when, what, sub, col) in enumerate(pts):
        x = x0 + i * (x1 - x0) / (len(pts) - 1)
        last = i == len(pts) - 1
        body += (f'<circle cx="{x:.0f}" cy="{y}" r="12" fill="{BG}" stroke="{col}" stroke-width="4"/>'
                 + (f'<circle cx="{x:.0f}" cy="{y}" r="12" fill="none" stroke="{col}" stroke-width="2"><animate attributeName="r" values="12;34" dur="2s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;0" dur="2s" repeatCount="indefinite"/></circle>' if last else '')
                 + text(x, y - 30, when, 13, col, .9, anchor='middle', ls=3) + text(x, y + 48, what, 16, col, anchor='middle', font=SANS, weight=900, ls=1.5) + text(x, y + 70, sub, 13, op=.6, anchor='middle'))
    body += mini('timeline', x0 + 60, y - 4, '#ffffff')
    return svg(W, H, body, 'The road so far: 2022 co-producer (HBO Max); 2026 OpenSSF Silver for Ratchet and Crimp; patents pending; 10 November 2026 Clockford private beta.')


# ================================================================ S10 THE WALL
def wall():
    H = 640
    img = uri(A / 'cast' / 'wall-scene.webp')
    iw, ih = 1002, 1360
    sh = H; sw = iw * sh / ih
    sx = (W - sw) / 2 + 140
    defs = (f'<linearGradient id="lf" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".22" stop-color="#fff"/><stop offset=".78" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<mask id="m"><rect x="{sx}" y="0" width="{sw}" height="{H}" fill="url(#lf)"/></mask>'
            f'<filter id="amb" x="0" y="0" width="100%" height="100%"><feGaussianBlur stdDeviation="40"/><feColorMatrix type="matrix" values=".55 0 0 0 0  0 .5 0 0 0  0 0 .45 0 0  0 0 0 1 0"/></filter>'
            f'<clipPath id="cl"><rect width="{W}" height="{H}" rx="22"/></clipPath>'
            f'<linearGradient id="vg" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="{BG}" stop-opacity=".6"/><stop offset=".25" stop-color="{BG}" stop-opacity="0"/><stop offset=".8" stop-color="{BG}" stop-opacity="0"/><stop offset="1" stop-color="{BG}" stop-opacity=".9"/></linearGradient>')
    body = (f'<g clip-path="url(#cl)"><rect width="{W}" height="{H}" fill="{BG}"/>'
            f'<image href="{uri(A / "cast" / "wall-ambient.webp")}" x="-80" y="-140" width="{W + 160}" height="{H + 280}" preserveAspectRatio="xMidYMid slice" filter="url(#amb)" opacity=".75"/>'
            f'<rect width="{W}" height="{H}" fill="{BG}" opacity=".35"/>'
            f'<image href="{img}" x="{sx:.0f}" y="0" width="{sw:.0f}" height="{sh}" mask="url(#m)"/>{mini("wall", sx + sw * .8, H * .92, "#ffdca0")}'
            f'<rect width="{W}" height="{H}" fill="url(#vg)"/>'
            + text(150, 250, 'THE WOLF', 64, '#fff', font=SANS, weight=900, ls=4) + text(150, 320, 'FOUND', 64, '#fff', font=SANS, weight=900, ls=4)
            + text(150, 390, 'THE WALL.', 64, YELLOW, font=SANS, weight=900, ls=4) + text(154, 440, 'every system has one. he always finds it.', 16, op=.65)
            + rail(H, '#fff', '#fff') + '</g>' + f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="none" stroke="#fff" stroke-opacity=".1"/>')
    return svg(W, H, body, 'The wolf found the wall: a wolf pup with cheese looks up at the Deimos mark sprayed on a concrete wall.', defs)


# ================================================================ S11 FOOTER: the last stop, and the finders ledger
def ledger():
    p = A / 'ledger.json'
    return json.loads(p.read_text()) if p.exists() else {'yesterday': [], 'all': [], 'day': None}


def footer(light=False):
    H, floor = 340, 270
    fg = INK if light else '#fff'
    L = ledger()
    defs = f'<pattern id="gridF" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="{INK}" stroke-opacity=".10"/></pattern>'
    body = (f'<rect width="{W}" height="{H}" rx="22" fill="#fff"/><rect width="{W}" height="{H}" rx="22" fill="url(#gridF)"/>' if light else card_bg(H))
    body += (f'<rect x="{RAIL_X + 20}" y="{floor + 3}" width="{W - 240}" height="{H - floor - 30}" fill="{"#eef2ff" if light else "#0a0812"}"/>'
             f'<path d="M{RAIL_X},0 L{RAIL_X},{floor - 20} Q{RAIL_X},{floor} {RAIL_X + 20},{floor} L{W - 110},{floor}" fill="none" stroke="{fg}" stroke-width="6"/>'
             f'<circle r="5" fill="{PINK}" filter="url(#glow)"><animateMotion path="M{RAIL_X},0 L{RAIL_X},{floor} L{W - 110},{floor}" dur="6s" repeatCount="indefinite"/></circle>')
    tx, ty = W - 110, floor
    body += (f'<circle cx="{tx}" cy="{ty}" r="46" fill="{"#fff" if light else BG}" stroke="{PINK}" stroke-width="6"/>'
             f'<circle cx="{tx}" cy="{ty}" r="46" fill="none" stroke="{PINK}" stroke-width="2"><animate attributeName="r" values="46;72" dur="2.4s" repeatCount="indefinite"/><animate attributeName="opacity" values=".8;0" dur="2.4s" repeatCount="indefinite"/></circle>'
             + text(tx, ty - 4, '10', 26, PINK, font=SANS, weight=900, anchor='middle') + text(tx, ty + 18, 'NOV', 13, PINK, weight=700, anchor='middle', ls=3))
    rg, _ = ground('rook', 250, floor, 214, '#ffffff' if light else CYAN, 1, night=not light)
    desk = (f'<rect x="300" y="{floor - 72}" width="170" height="10" rx="3" fill="#6d5233"/><rect x="310" y="{floor - 62}" width="10" height="62" fill="#4e3a23"/><rect x="450" y="{floor - 62}" width="10" height="62" fill="#4e3a23"/>'
            f'<rect x="330" y="{floor - 90}" width="110" height="18" rx="2" fill="#efeadd" transform="rotate(-4 385 {floor - 81})"/>'
            + text(385, floor - 77, 'FINDERS', 8, '#7a6a4a', weight=700, anchor='middle', ls=2, extra=f'transform="rotate(-4 385 {floor - 81})"'))
    yest = L.get('yesterday', [])[:8]
    acc = INK if light else YELLOW
    led = text(520, 60, 'FINDERS LEDGER', 13, fg, .55, ls=6) + text(520, 92, 'FOUND HIM YESTERDAY', 12, acc, .9, ls=3, weight=700)
    led += (''.join(text(520 + (i // 4) * 210, 120 + (i % 4) * 22, '@' + h, 14, fg, .9) for i, h in enumerate(yest)) if yest
            else text(520, 122, 'nobody yesterday. he’s good.', 14, fg, .7, extra='font-style="italic"'))
    led += text(520, 222, f'ALL-TIME FINDERS: {len(L.get("all", []))}', 12, fg, .6, ls=3) + text(520, 244, 'found him? click here and tell Rook the word.', 12, acc, .8)
    wg, (wx, wy, ww, wh) = ground('wolf-lookback', 985, floor, 152, '#ffe9c2' if light else PINK, -1, night=not light)
    lip = f'<rect x="{RAIL_X + 20}" y="{floor + 2}" width="{W - 240}" height="5" fill="{"#dfe6ff" if light else "#16121f"}"/>'
    copy = text(150, H - 26, 'daylight edition. the night shift left you a note: come back tomorrow.' if light else 'built at 3 a.m., on purpose. the agents never sleep. neither do i.', 14, fg, .72)
    body += rg + desk + wg + lip + pill(wx + ww * .5, wy - 12, 'same time tomorrow?', INK if light else PINK, '#fff', 14, 'middle') + led + copy + mini('footer', 760, floor, PINK, not light)
    body += f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="none" stroke="{fg}" stroke-opacity=".12"/>'
    return svg(W, H, body, 'Last stop: 10 November. The finders ledger for today’s wolf hunt.', defs)


# ================================================================ dividers: the line keeps going (a hunt slot each)
def divider(k, light=False):
    H = 110
    col = [CYAN, PINK, GOLD][k - 1]
    fg = INK if light else col
    body = (f'<line x1="{RAIL_X}" y1="0" x2="{RAIL_X}" y2="{H}" stroke="{INK if light else "#fff"}" stroke-width="6" opacity=".85"/>'
            f'<circle r="5" fill="{fg}" filter="url(#glow)"><animateMotion path="M{RAIL_X},0 L{RAIL_X},{H}" dur="1.2s" repeatCount="indefinite"/></circle>'
            f'<line x1="{RAIL_X + 30}" y1="{H - 20}" x2="{W - 40}" y2="{H - 20}" stroke="{fg}" stroke-opacity=".22"/>')
    body += mini(f'div{k}', 300 + seeded(f'div{k}x').randint(0, 760), H - 20, col, not light)
    return svg(W, H, body, '')


# ================================================================ the stack (folded away in <details>)
STACK = [
    ('LANGUAGES', [('TypeScript', 'typescript', '#3178C6'), ('JavaScript', 'javascript', '#F7DF1E'), ('Python', 'python', '#FFD43B'),
                   ('Swift', 'swift', '#F05138'), ('Bash', 'gnubash', '#4EAA25'), ('HTML', 'html5', '#E34F26'), ('CSS', 'css3', '#2965F1')]),
    ('BUILD', [('Node.js', 'nodedotjs', '#5FA04E'), ('Three.js', 'threedotjs', '#ffffff'), ('Vite', 'vite', '#8B8FFF'),
               ('PostgreSQL', 'postgresql', '#6D8FFF'), ('Zod', 'zod', '#7AA2FF'), ('MCP', None, '#ffffff')]),
    ('SHIP', [('Docker', 'docker', '#2496ED'), ('Cloudflare', 'cloudflare', '#F38020'), ('Vercel', 'vercel', '#ffffff'),
              ('Fly.io', 'flydotio', '#A78BFA'), ('Actions', 'githubactions', '#2088FF')]),
    ('MAKE', [('Blender', 'blender', '#E87D0D'), ('Claude', 'claude', '#D97757'), ('Passkeys', 'webauthn', '#8B7BFF')]),
]


def icon_path(slug):
    return re.search(r'<path d="([^"]+)"', (ICONS / f'{slug}.svg').read_text()).group(1)


def stack():
    tile, gap = 74, 18
    body, y, n = '', 64, 0
    for group, items in STACK:
        body += text(40, y + 44, group, 13, op=.5, ls=5)
        x = 200
        for label, slug, col in items:
            n += 1
            glyph = (f'<g transform="translate({x + tile / 2 - 18} {y + 14}) scale(1.5)"><path d="{icon_path(slug)}" fill="{col}"/></g>' if slug
                     else f'<g transform="translate({x + tile / 2} {y + 32})" fill="none" stroke="{col}" stroke-width="3" stroke-linecap="round"><path d="M-16,-6 L-4,-16 L8,-4"/><path d="M-8,4 L4,-6 L16,6"/><path d="M-12,12 L0,2"/></g>')
            body += (f'<rect x="{x}" y="{y}" width="{tile}" height="{tile}" rx="16" fill="{PANEL}" stroke="{col}" stroke-opacity=".35"/>'
                     f'<rect x="{x}" y="{y}" width="{tile}" height="{tile}" rx="16" fill="{col}" opacity="0"><animate attributeName="opacity" values="0;.22;0" begin="{n * .18:.2f}s;{n * .18 + 12:.2f}s" dur="1.4s"/></rect>'
                     + glyph + text(x + tile / 2, y + tile + 20, label, 12, op=.75, anchor='middle'))
            x += tile + gap + 22
        y += tile + 56
    H = y + 10
    return svg(W, H, card_bg(H) + body, 'The stack: TypeScript, JavaScript, Python, Swift, Bash, HTML, CSS; Node.js, Three.js, Vite, PostgreSQL, Zod, MCP; Docker, Cloudflare, Vercel, Fly.io, GitHub Actions; Blender, Claude, passkeys.')


# ================================================================ the ledger, kept by the daily Action from "found the wolf" issues
def update_ledger():
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    if not (token and os.environ.get('GITHUB_ACTIONS')): return
    api = f'https://api.github.com/repos/{REPO}'
    hdr = {'Authorization': f'bearer {token}', 'Accept': 'application/vnd.github+json'}

    def call(method, url, data=None):
        req = urllib.request.Request(url, json.dumps(data).encode() if data is not None else None, hdr, method=method)
        return json.load(urllib.request.urlopen(req, timeout=30))
    L = ledger()
    ok = {word_for(TODAY), word_for(TODAY - dt.timedelta(days=1))}
    found = []
    for issue in call('GET', f'{api}/issues?labels=found-the-wolf&state=open&per_page=100'):
        who = issue['user']['login']
        said = re.sub(r'[^A-Z]', '', (issue.get('body') or '').upper().replace('È', 'E').replace('É', 'E'))
        right = any(w in said for w in ok)
        try:
            call('POST', f'{api}/issues/{issue["number"]}/comments', {'body': '**Rook:** ' + ('Logged. He says hi.' if right else 'Wrong word. He’s still out there.')})
            call('PATCH', f'{api}/issues/{issue["number"]}', {'state': 'closed', 'state_reason': 'completed' if right else 'not_planned'})
        except Exception as e:
            print('ledger:', e)
        if right and who not in found: found.append(who)
    if L.get('day') != TODAY.isoformat():
        L = {'yesterday': found, 'all': sorted(set(L.get('all', [])) | set(found)), 'day': TODAY.isoformat()}
    else:
        L['yesterday'] = sorted(set(L['yesterday']) | set(found)); L['all'] = sorted(set(L.get('all', [])) | set(found))
    (A / 'ledger.json').write_text(json.dumps(L, indent=1))


def main():
    if '--daily' in sys.argv: update_ledger()
    out = {'hero-dark.svg': hero(False), 'hero-light.svg': hero(True), 'board.svg': board(),
           'st-clockford.svg': st_clockford(), 'st-ratchet.svg': st_ratchet(), 'st-crimp.svg': st_crimp(), 'st-marklode.svg': st_marklode(), 'st-max.svg': st_max(),
           'rules.svg': rules(), 'how.svg': how(), 'terminal.svg': terminal(), 'cast.svg': cast_scene(), 'timeline.svg': timeline(), 'wall.svg': wall(),
           'footer-dark.svg': footer(False), 'footer-light.svg': footer(True), 'stack.svg': stack()}
    for k in (1, 2, 3):
        out[f'divider-{k}-dark.svg'] = divider(k, False); out[f'divider-{k}-light.svg'] = divider(k, True)
    st = stats()
    if st: out['stats.svg'] = st
    for name, s in out.items():
        (A / name).write_text(s, encoding='utf-8')
        print(f'{name:22} {len(s) // 1024:5d} KB')
    print('hunt slot:', HUNT['slot'], '·', HUNT['pose'])


if __name__ == '__main__':
    main()
