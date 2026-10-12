# Builds every SVG on the profile. Standard library only, so the daily GitHub Action can run it.
#   python3 tools/profile.py            all art (stats from the API if GH_TOKEN/GITHUB_TOKEN or `gh` is available)
#   python3 tools/profile.py --daily    the same; the wolf, the countdown and the stats change with the date
import base64, datetime as dt, hashlib, json, math, os, pathlib, random, re, subprocess, urllib.request
from xml.sax.saxutils import escape as esc

ROOT = pathlib.Path(__file__).resolve().parent.parent
A = ROOT / 'assets'
ICONS = ROOT / 'src' / 'icons'
USER = 'thearchitect0x-glitch'
BETA = dt.date(2026, 11, 10)
TODAY = dt.date.fromisoformat(os.environ.get('PROFILE_DAY', dt.date.today().isoformat()))
day_rng = random.Random(int(hashlib.sha256(TODAY.isoformat().encode()).hexdigest(), 16))

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
SANS = "'Helvetica Neue',Helvetica,Arial,sans-serif"
BG, PANEL = '#05040a', '#0c0a16'
GOLD, GREEN, PINK, CYAN, ORANGE, VIOLET, YELLOW = '#F7CD45', '#39ff88', '#ff2bd6', '#00e5ff', '#ff7a1a', '#7a5cff', '#fff23a'
ACID = [PINK, VIOLET, CYAN, GREEN, YELLOW, ORANGE, PINK]


def uri(path, mime=None):
    p = pathlib.Path(path)
    mime = mime or {'.jpg': 'image/jpeg', '.png': 'image/png', '.svg': 'image/svg+xml', '.webp': 'image/webp'}[p.suffix]
    return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"


def cast(name):
    return uri(A / 'cast' / f'{name}.webp')


def size_of(name):
    b = (A / 'cast' / f'{name}.webp').read_bytes()
    # VP8X header: canvas width/height minus one, 24-bit little endian at bytes 24..29
    if b[12:16] == b'VP8X':
        return 1 + int.from_bytes(b[24:27], 'little'), 1 + int.from_bytes(b[27:30], 'little')
    raise ValueError(name)


def svg(w, h, body, label, defs=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{esc(label)}">'
            f'<defs>{GLOW}{defs}</defs>{body}</svg>')


GLOW = ('<filter id="glow" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="5" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        '<filter id="soft" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="18"/></filter>'
        '<filter id="hue"><feColorMatrix type="hueRotate" values="0"><animate attributeName="values" values="0;360" dur="16s" repeatCount="indefinite"/></feColorMatrix></filter>'
        '<filter id="shadow" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#000" flood-opacity=".7"/></filter>')


def frame(w, h, col='#fff', op=.10, rx=22):
    return (f'<rect width="{w}" height="{h}" rx="{rx}" fill="{BG}"/>'
            f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{rx}" fill="none" stroke="{col}" stroke-opacity="{op}"/>')


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


def text(x, y, s, size=16, col='#fff', op=1, font=MONO, weight=400, anchor='start', ls=0, extra=''):
    return (f'<text x="{x}" y="{y}" fill="{col}" fill-opacity="{op}" font-family="{font}" font-size="{size}" font-weight="{weight}" '
            f'text-anchor="{anchor}" letter-spacing="{ls}" {extra}>{esc(s)}</text>')


def stars(w, h, n, rng):
    return ''.join(f'<circle cx="{rng.randint(0, w)}" cy="{rng.randint(0, h)}" r="{rng.choice((.7, 1, 1.4))}" fill="#fff">'
                   f'<animate attributeName="opacity" values=".1;.8;.1" dur="{rng.uniform(2, 6):.1f}s" begin="{rng.uniform(0, 4):.1f}s" repeatCount="indefinite"/></circle>'
                   for _ in range(n))


# ---------------------------------------------------------------- hero
def hero():
    rng = random.Random(11)
    W, H = 1280, 460
    cx, cy = 300, 230
    blobs = ''
    for i, (x, y, r) in enumerate([(160, 120, 210), (420, 340, 230), (760, 110, 200), (1080, 330, 240), (620, 420, 180)]):
        dx, dy = rng.randint(-90, 90), rng.randint(-60, 60)
        blobs += (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{ACID[i]}">{cycle("fill", i + 1, 11 + i * 2)}'
                  f'<animateTransform attributeName="transform" type="translate" values="0 0;{dx} {dy};0 0" dur="{13 + i * 3}s" repeatCount="indefinite"/></circle>')

    def mandala(n, r0, r1, w, dur, rev, grad):
        petal = f'M0,{-r0} C{w},{-(r0 + r1) / 2} {w},{-(r0 + r1) / 2 - 10} 0,{-r1} C{-w},{-(r0 + r1) / 2 - 10} {-w},{-(r0 + r1) / 2} 0,{-r0}Z'
        ps = ''.join(f'<path d="{petal}" transform="rotate({360 * i / n})"/>' for i in range(n))
        return (f'<g transform="translate({cx} {cy})"><g fill="url(#{grad})" fill-opacity=".55" stroke="#fff" stroke-opacity=".18">{ps}'
                f'<animateTransform attributeName="transform" type="rotate" from="0" to="{-360 if rev else 360}" dur="{dur}s" repeatCount="indefinite"/></g></g>')

    def gear(gx, gy, r, teeth, dur, rev=False):
        pts = ' '.join(f'{gx + (r if i % 4 in (0, 1) else r * .82) * math.cos(2 * math.pi * i / (teeth * 4)):.1f},'
                       f'{gy + (r if i % 4 in (0, 1) else r * .82) * math.sin(2 * math.pi * i / (teeth * 4)):.1f}' for i in range(teeth * 4))
        return (f'<g><polygon points="{pts}" fill="none" stroke="#fff" stroke-width="2.2"/><circle cx="{gx}" cy="{gy}" r="{r * .35:.1f}" fill="none" stroke="#fff" stroke-width="2"/>'
                f'<animateTransform attributeName="transform" type="rotate" from="0 {gx} {gy}" to="{"-360" if rev else "360"} {gx} {gy}" dur="{dur}s" repeatCount="indefinite"/></g>')

    orbits = ''
    for k, rot in enumerate((0, 60, 120)):
        orbits += (f'<g transform="rotate({rot} {cx} {cy})"><path id="orb{k}" d="M{cx - 200},{cy} a200,62 0 1,0 400,0 a200,62 0 1,0 -400,0" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="2" stroke-dasharray="2 7"/>'
                   f'<circle r="7" fill="#fff"><animateMotion dur="{4 + k * 1.3}s" repeatCount="indefinite"><mpath href="#orb{k}"/></animateMotion></circle></g>')
    ticks = ''.join(f'<line x1="{cx}" y1="{cy - 222}" x2="{cx}" y2="{cy - (204 if i % 5 else 194)}" transform="rotate({i * 6} {cx} {cy})"/>' for i in range(60))
    title = 'THE ARCHITECT'
    glitch = lambda col, xs: (f'<text x="600" y="205" fill="{col}" opacity=".85" font-family="{SANS}" font-size="66" font-weight="900" letter-spacing="3">{title}'
                              f'<animate attributeName="x" values="{xs}" dur="2.6s" calcMode="discrete" repeatCount="indefinite"/></text>')
    ww, wh = size_of('wolf-cheesehat')
    sc = 190 / wh
    wolf = (f'<g><animateTransform attributeName="transform" type="translate" values="0 0;0 0;0 -150;0 -150;0 0;0 0" keyTimes="0;.55;.6;.82;.87;1" dur="15s" repeatCount="indefinite"/>'
            f'<image href="{cast("wolf-cheesehat")}" x="1080" y="{H + 10}" width="{ww * sc:.0f}" height="190" filter="url(#shadow)"/>'
            f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;.6;.62;.8;.82;1" dur="15s" repeatCount="indefinite"/>'
            f'<rect x="938" y="{H + 20}" width="128" height="34" rx="17" fill="{YELLOW}"/>{text(1002, H + 43, "psst. 🧀", 16, BG, anchor="middle", weight=700)}</g></g>')
    defs = (f'<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="55"/></filter>'
            f'<radialGradient id="pet"><stop offset="0" stop-color="#fff">{cycle("stop-color", 2, 7)}</stop><stop offset="1" stop-color="{PINK}">{cycle("stop-color", 4, 7)}</stop></radialGradient>'
            f'<radialGradient id="pet2"><stop offset="0" stop-color="{CYAN}">{cycle("stop-color", 3, 5)}</stop><stop offset="1" stop-color="{VIOLET}" stop-opacity=".2">{cycle("stop-color", 5, 5)}</stop></radialGradient>'
            f'<linearGradient id="tg" x1="0" x2="1"><stop offset="0" stop-color="{YELLOW}">{cycle("stop-color", 1, 6)}</stop><stop offset=".5" stop-color="#fff"/><stop offset="1" stop-color="{CYAN}">{cycle("stop-color", 4, 6)}</stop></linearGradient>'
            f'<clipPath id="type"><rect x="600" y="296" width="0" height="30"><animate attributeName="width" values="0;480;480;480;0" keyTimes="0;.25;.4;.9;1" dur="11s" repeatCount="indefinite"/></rect></clipPath>'
            f'<clipPath id="type2"><rect x="600" y="327" width="0" height="30"><animate attributeName="width" values="0;0;320;320;0" keyTimes="0;.28;.42;.9;1" dur="11s" repeatCount="indefinite"/></rect></clipPath>'
            f'<clipPath id="card"><rect width="{W}" height="{H}" rx="22"/></clipPath>'
            f'<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".22"/></pattern>')
    body = f'''<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="{BG}"/>
<g filter="url(#hue)"><g filter="url(#blur)" opacity=".42">{blobs}</g>{mandala(12, 40, 190, 46, 48, False, "pet")}{mandala(24, 120, 236, 22, 70, True, "pet2")}
<g stroke="#fff" stroke-opacity=".7" stroke-width="2">{ticks}<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="60s" repeatCount="indefinite"/></g>
{gear(92, 392, 34, 12, 9)}{gear(146, 404, 22, 8, 6, True)}{gear(1230, 60, 26, 10, 8)}</g>
<g filter="url(#glow)">{orbits}{deimos(cx, cy, .62)}</g>
{glitch(CYAN, "597;600;603;596;600;600;601")}{glitch(PINK, "603;600;597;604;600;600;599")}
<text x="600" y="205" fill="url(#tg)" font-family="{SANS}" font-size="66" font-weight="900" letter-spacing="3">{title}</text>
{text(604, 252, "CO-FOUNDER · DEIMOS AI LLC", 21, op=.85, ls=3)}
<g clip-path="url(#type)">{text(604, 318, "> I see systems laid out in front of me.", 19, GREEN)}</g>
<g clip-path="url(#type2)">{text(604, 348, "> Then I build the answer.", 19, GREEN)}</g>
<rect x="604" y="358" width="11" height="18" fill="{GREEN}"><animate attributeName="opacity" values="1;0" dur=".8s" calcMode="discrete" repeatCount="indefinite"/></rect>
{text(604, 410, "CLOCKFORD · RATCHET · CRIMP · MARKLODE · M.A.X", 15, op=.7, ls=4)}
{wolf}
<rect width="{W}" height="{H}" fill="url(#scan)"/></g>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="none" stroke="#fff" stroke-opacity=".12"/>'''
    return svg(W, H, body, 'The Architect: co-founder, Deimos AI LLC. Builder of Clockford, Ratchet, Crimp, Marklode and M.A.X.', defs)


# ---------------------------------------------------------------- now (departure board)
def now():
    W, H = 1280, 300
    days = (BETA - TODAY).days
    beta = f'PRIVATE BETA IN {days} DAYS' if days > 1 else ('PRIVATE BETA TOMORROW' if days == 1 else 'PRIVATE BETA IS OPEN')
    rows = [('CLOCKFORD', GOLD, beta, 'patent pending'),
            ('RATCHET', GREEN, 'LIVE · 1,000 EFFECTS / MONTH FREE', 'ratchetgate.com'),
            ('CRIMP', PINK, 'OPEN SOURCE · PATENT PENDING', 'github'),
            ('MARKLODE', CYAN, 'TAKING IDEAS · 24–72 H', 'marklode.com'),
            ('M.A.X', ORANGE, 'OFFLINE-FIRST · IN THE LAB', 'deimoscore.com')]
    body = frame(W, H)
    body += text(40, 50, 'NOW', 14, op=.55, ls=6) + text(W - 40, 50, f'BOARD UPDATED {TODAY.strftime("%d %b %Y").upper()}', 12, op=.35, anchor='end', ls=3)
    body += f'<line x1="40" y1="64" x2="{W - 40}" y2="64" stroke="#fff" stroke-opacity=".08"/>'
    for i, (name, col, status, where) in enumerate(rows):
        y = 104 + i * 40
        t = .3 + i * .35
        # board cells behind the name
        cells = ''.join(f'<rect x="{78 + k * 22}" y="{y - 22}" width="19" height="30" rx="3" fill="#15121f"/>' for k in range(10))
        body += (f'<circle cx="52" cy="{y - 7}" r="6" fill="{col}"><animate attributeName="opacity" values="1;.25;1" dur="{1.6 + i * .3:.1f}s" repeatCount="indefinite"/></circle>{cells}'
                 + ''.join(f'<text x="{88 + k * 22}" y="{y}" text-anchor="middle" fill="{col}" font-family="{MONO}" font-size="19" font-weight="700" opacity="0">{esc(ch)}'
                           f'<animate attributeName="opacity" values="0;1" begin="{t + k * .05:.2f}s" dur=".01s" fill="freeze"/></text>' for k, ch in enumerate(name))
                 + f'<clipPath id="st{i}"><rect x="320" y="{y - 24}" height="32" width="0"><animate attributeName="width" from="0" to="760" begin="{t + .5:.2f}s" dur=".9s" fill="freeze"/></rect></clipPath>'
                 + f'<g clip-path="url(#st{i})">{text(320, y, status, 18, "#fff", .92, ls=2)}</g>'
                 + text(W - 40, y, where, 13, col, .7, anchor='end', ls=1))
    return svg(W, H, body, f'Now: Clockford {beta.lower()}; Ratchet live; Crimp open source; Marklode taking ideas; M.A.X in the lab.')


# ---------------------------------------------------------------- systems map
PRODUCTS = [
    ('CLOCKFORD', GOLD, 'see · approve · stop your AI agents from your phone', 'patent pending', (300, 130)),
    ('RATCHET', GREEN, 'every real-world effect, at most once', 'OpenSSF Silver', (980, 130)),
    ('CRIMP', PINK, 'decisions that withdraw themselves when a fact breaks', 'patent pending · OpenSSF Silver', (990, 420)),
    ('MARKLODE', CYAN, 'diligence before the pitch, in 24 to 72 hours', 'marklode.com', (290, 420)),
    ('M.A.X', ORANGE, 'behavior, read against each person’s own baseline', 'deimoscore.com', (640, 520)),
]


def systems():
    rng = random.Random(5)
    W, H = 1280, 680
    cx, cy = 640, 300
    rules = 'PEOPLE STAY IN CHARGE OF WHAT MATTERS  ✦  ASSUME SOMETHING IS ALREADY INSIDE  ✦  IF IT MATTERS, MAKE IT PROVABLE  ✦  BEND, DON’T BREAK  ✦  '
    rings = ''.join(f'<ellipse cx="{cx}" cy="{cy}" rx="{r * 1.9:.0f}" ry="{r * .95:.0f}" fill="none" stroke="#fff" stroke-opacity="{.10 + .05 * i:.2f}" stroke-width="1.5" stroke-dasharray="3 9">'
                    f'<animate attributeName="stroke-dashoffset" values="0;{120 if i % 2 else -120}" dur="{6 + i * 2}s" repeatCount="indefinite"/></ellipse>' for i, r in enumerate((150, 215, 280)))
    cm = uri(A / 'clockford-mark.svg')
    a_, b_ = 618, 318
    RING = math.pi * (3 * (a_ + b_) - math.sqrt((3 * a_ + b_) * (a_ + 3 * b_))) - 4
    planets = ''
    for k, (name, col, line, tag, (px, py)) in enumerate(PRODUCTS):
        inner = (f'<clipPath id="cmc{k}"><circle cx="{px}" cy="{py}" r="26"/></clipPath><image href="{cm}" x="{px - 26}" y="{py - 26}" width="52" height="52" clip-path="url(#cmc{k})"/>' if name == 'CLOCKFORD'
                 else text(px, py + 8, name[0], 22, BG, font=SANS, weight=900, anchor='middle'))
        planets += f'''<path id="beam{k}" d="M{cx},{cy} L{px},{py}" stroke="{col}" stroke-opacity=".35" stroke-width="1.5"/>
<circle r="4.5" fill="{col}"><animateMotion dur="{1.8 + k * .35:.2f}s" repeatCount="indefinite" begin="{k * .4:.1f}s"><mpath href="#beam{k}"/></animateMotion></circle>
<circle cx="{px}" cy="{py}" r="40" fill="{col}" opacity=".25" filter="url(#soft)"><animate attributeName="r" values="34;48;34" dur="{2.5 + k * .4:.1f}s" repeatCount="indefinite"/></circle>
<circle cx="{px}" cy="{py}" r="30" fill="{col}"/>{inner}
{text(px, py + 66, name, 24, col, font=SANS, weight=900, anchor="middle", ls=3)}{text(px, py + 88, line, 14, op=.88, anchor="middle")}{text(px, py + 107, tag.upper(), 12, op=.5, anchor="middle", ls=2)}'''
    defs = (f'<radialGradient id="neb"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".55"/><stop offset=".5" stop-color="{PINK}" stop-opacity=".18"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></radialGradient>'
            f'<path id="rules" d="M{cx - 618},{cy + 40} a618,318 0 1,1 1236,0 a618,318 0 1,1 -1236,0"/>')
    body = (frame(W, H) + stars(W, H, 90, rng) + f'<g filter="url(#hue)"><ellipse cx="{cx}" cy="{cy}" rx="560" ry="300" fill="url(#neb)"/>{rings}</g>'
            f'<text font-family="{MONO}" font-size="13" fill="#fff" fill-opacity=".45"><textPath href="#rules" textLength="{RING:.0f}" lengthAdjust="spacing">{esc(rules * 2)}</textPath></text>'
            f'<circle r="4" fill="{YELLOW}" filter="url(#glow)"><animateMotion dur="40s" repeatCount="indefinite"><mpath href="#rules"/></animateMotion></circle>'
            + planets + f'<circle cx="{cx}" cy="{cy}" r="78" fill="{BG}" stroke="#fff" stroke-opacity=".2"/>'
            f'<g filter="url(#hue)"><circle cx="{cx}" cy="{cy}" r="92" fill="none" stroke="{PINK}" stroke-width="2" stroke-dasharray="1 11"><animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="18s" repeatCount="indefinite"/></circle></g>'
            + deimos(cx, cy, .42) + text(cx, cy + 118, 'DEIMOS AI', 13, op=.8, anchor='middle', ls=6))
    return svg(W, H, body, 'The system map: Deimos at the core; Clockford, Ratchet, Crimp, Marklode and M.A.X in orbit; four rules around the edge.', defs)


# ---------------------------------------------------------------- product cards
def motif(kind, col, x, y):
    """A small animated emblem for each product, centred at (x, y), ~180px."""
    if kind == 'CLOCKFORD':
        dots = ''.join(f'<g transform="rotate({i * 60} {x} {y})"><circle cx="{x}" cy="{y - 76}" r="7" fill="#fff" fill-opacity=".35">'
                       f'<animate attributeName="fill" values="#ffffff;#ffffff;{GREEN};{GREEN};#ffffff" keyTimes="0;{i / 6:.2f};{i / 6 + .05:.2f};.95;1" dur="6s" repeatCount="indefinite"/>'
                       f'<animate attributeName="fill-opacity" values=".35;.35;1;1;.35" keyTimes="0;{i / 6:.2f};{i / 6 + .05:.2f};.95;1" dur="6s" repeatCount="indefinite"/></circle></g>' for i in range(6))
        hand = (f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y - 64}" stroke="{col}" stroke-width="3" stroke-linecap="round">'
                f'<animateTransform attributeName="transform" type="rotate" from="0 {x} {y}" to="360 {x} {y}" dur="6s" repeatCount="indefinite"/></line>')
        return (f'<circle cx="{x}" cy="{y}" r="76" fill="none" stroke="{col}" stroke-opacity=".3" stroke-dasharray="2 6"/>{dots}{hand}'
                f'<clipPath id="cfm"><circle cx="{x}" cy="{y}" r="34"/></clipPath><image href="{uri(A / "clockford-mark.svg")}" x="{x - 34}" y="{y - 34}" width="68" height="68" clip-path="url(#cfm)"/>')
    if kind == 'RATCHET':
        n, r = 14, 62
        pts = ' '.join(f'{x + (r if i % 2 == 0 else r - 16) * math.cos(2 * math.pi * (i // 2 + (.75 if i % 2 else 0)) / n):.1f},'
                       f'{y + (r if i % 2 == 0 else r - 16) * math.sin(2 * math.pi * (i // 2 + (.75 if i % 2 else 0)) / n):.1f}' for i in range(n * 2))
        steps = ';'.join(f'{k * 360 / n:.2f} {x} {y}' for k in range(n + 1))
        return (f'<g><polygon points="{pts}" fill="none" stroke="{col}" stroke-width="3" stroke-linejoin="round"/><circle cx="{x}" cy="{y}" r="18" fill="{col}"/>'
                f'<animateTransform attributeName="transform" type="rotate" values="{steps}" dur="{n * .55:.2f}s" calcMode="discrete" repeatCount="indefinite"/></g>'
                f'<path d="M{x + 92},{y - 70} L{x + 50},{y - 44}" stroke="#fff" stroke-width="5" stroke-linecap="round"/>'
                + text(x, y + 104, '× 1', 22, col, weight=700, anchor='middle', ls=2))
    if kind == 'CRIMP':
        lines = ''.join(f'<rect x="{x - 52}" y="{y - 58 + k * 16}" width="{104 - (k % 3) * 18}" height="6" rx="3" fill="#fff" fill-opacity=".25"/>' for k in range(6))
        stamp = (f'<g opacity="0" transform="rotate(-12 {x} {y + 10})"><rect x="{x - 66}" y="{y - 8}" width="132" height="40" rx="6" fill="none" stroke="{col}" stroke-width="4"/>'
                 + text(x, y + 21, 'SEALED', 20, col, weight=900, anchor='middle', ls=4)
                 + f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;.3;.32;.9;1" dur="4s" repeatCount="indefinite"/>'
                 f'<animateTransform attributeName="transform" type="scale" additive="sum" values="1;1;1.25 1.25;1;1" keyTimes="0;.3;.31;.36;1" dur="4s" repeatCount="indefinite"/></g>')
        return f'<rect x="{x - 70}" y="{y - 80}" width="140" height="170" rx="8" fill="#15121f" stroke="#fff" stroke-opacity=".2"/>{lines}{stamp}'
    if kind == 'MARKLODE':
        bars = ''.join(f'<rect x="{x - 80}" y="{y - 60 + k * 20}" width="{160 - (k * 37) % 70}" height="8" rx="4" fill="#fff" fill-opacity=".18"/>' for k in range(7))
        hits = ''.join(f'<rect x="{x - 80}" y="{y - 60 + k * 20}" width="{160 - (k * 37) % 70}" height="8" rx="4" fill="{col}" opacity="0">'
                       f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;{t:.2f};{t + .04:.2f};.92;1" dur="5s" repeatCount="indefinite"/></rect>' for k, t in ((1, .2), (4, .5), (6, .75)))
        lens = (f'<g><circle cx="{x - 40}" cy="{y - 40}" r="30" fill="{col}" fill-opacity=".08" stroke="#fff" stroke-width="4"/><line x1="{x - 18}" y1="{y - 18}" x2="{x + 6}" y2="{y + 6}" stroke="#fff" stroke-width="7" stroke-linecap="round"/>'
                f'<animateTransform attributeName="transform" type="translate" values="0 0;60 30;10 80;70 110;0 0" dur="5s" repeatCount="indefinite"/></g>')
        return bars + hits + lens
    if kind == 'M.A.X':
        def wave(seed, spike):
            r = random.Random(seed)
            pts = []
            for i in range(41):
                xx = x - 100 + i * 5
                yy = y + r.uniform(-9, 9) + (-52 if spike and i in (27, 28) else 0)
                pts.append(f'{xx:.0f},{yy:.0f}')
            return 'M' + ' L'.join(pts)
        vals = ';'.join(wave(s, s % 3 == 2) for s in range(6)) + ';' + wave(0, False)
        return (f'<rect x="{x - 104}" y="{y - 16}" width="208" height="32" rx="6" fill="{col}" fill-opacity=".10"/>'
                + text(x - 100, y - 24, 'BASELINE', 11, col, .7, ls=3)
                + f'<path d="{wave(0, False)}" fill="none" stroke="#fff" stroke-width="2.5" stroke-linejoin="round"><animate attributeName="d" values="{vals}" dur="6s" repeatCount="indefinite"/></path>'
                f'<circle cx="{x + 37}" cy="{y - 52}" r="9" fill="none" stroke="{col}" stroke-width="3" opacity="0"><animate attributeName="opacity" values="0;0;1;0;0;1;0" keyTimes="0;.33;.36;.5;.83;.86;1" dur="6s" repeatCount="indefinite"/></circle>')
    return ''


CARDS = [
    ('CLOCKFORD', GOLD, ['See, approve and stop your AI', 'agents from your phone, whichever', 'company built them.'], ['PATENT PENDING', 'BETA 10 NOV']),
    ('RATCHET', GREEN, ['The effect gate for AI agents.', 'A retried charge, deploy or email', 'happens at most once.'], ['OPENSSF SILVER', '1,000 FREE / MO']),
    ('CRIMP', PINK, ['Agents submit the rule and facts,', 'not a conclusion. Decisions withdraw', 'themselves when a fact breaks.'], ['PATENT PENDING', 'OPEN SOURCE', 'OPENSSF SILVER']),
    ('MARKLODE', CYAN, ['Startup diligence before the pitch:', 'competitors, overlapping patents,', 'the three strongest attacks, a verdict.'], ['24–72 H', 'SAMPLE ONLINE']),
    ('M.A.X', ORANGE, ['Offline-first behavioral analysis,', 'read against each person’s', 'own baseline.'], ['OFFLINE-FIRST', 'LITIGATION']),
]


def card(i):
    name, col, lines, chips = CARDS[i]
    W, H = 620, 300
    body = (f'<rect width="{W}" height="{H}" rx="20" fill="{PANEL}"/>'
            f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="20" fill="none" stroke="url(#edge)" stroke-width="2"/>'
            f'<circle cx="{W - 120}" cy="{H / 2 - 6}" r="120" fill="{col}" opacity=".10" filter="url(#soft)"/>'
            + text(32, 46, f'{i + 1:02d}', 13, col, .8, ls=3) + f'<line x1="62" y1="41" x2="110" y2="41" stroke="{col}" stroke-opacity=".5"/>'
            + text(30, 100, name, 42, col, font=SANS, weight=900, ls=2)
            + ''.join(text(32, 142 + k * 24, l, 15, op=.86) for k, l in enumerate(lines)))
    x = 32
    for c in chips:
        w = 16 + len(c) * 8.4
        body += f'<rect x="{x}" y="{H - 58}" width="{w:.0f}" height="28" rx="14" fill="none" stroke="{col}" stroke-opacity=".6"/>' + text(x + w / 2, H - 39, c, 11, col, anchor='middle', ls=1.5)
        x += w + 10
    body += motif(name, col, W - 120, H / 2 - 6)
    defs = f'<linearGradient id="edge" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{col}" stop-opacity=".9"/><stop offset=".45" stop-color="{col}" stop-opacity=".08"/><stop offset="1" stop-color="{col}" stop-opacity=".5"/></linearGradient>'
    return svg(W, H, body, f'{name}: {" ".join(lines)}', defs)


# ---------------------------------------------------------------- stack
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
    s = (ICONS / f'{slug}.svg').read_text()
    return re.search(r'<path d="([^"]+)"', s).group(1)


def stack():
    W = 1280
    tile, gap = 74, 18
    body, y, n = '', 64, 0
    for gi, (group, items) in enumerate(STACK):
        body += text(40, y + 44, group, 13, op=.5, ls=5)
        x = 200
        for label, slug, col in items:
            n += 1
            begin = n * .18
            glyph = (f'<g transform="translate({x + tile / 2 - 18} {y + 14}) scale(1.5)"><path d="{icon_path(slug)}" fill="{col}"/></g>' if slug
                     else f'<g transform="translate({x + tile / 2} {y + 32})" fill="none" stroke="{col}" stroke-width="3" stroke-linecap="round">'
                          f'<path d="M-16,-6 L-4,-16 L8,-4"/><path d="M-8,4 L4,-6 L16,6"/><path d="M-12,12 L0,2"/></g>')
            body += (f'<g><rect x="{x}" y="{y}" width="{tile}" height="{tile}" rx="16" fill="{PANEL}" stroke="{col}" stroke-opacity=".35"/>'
                     f'<rect x="{x}" y="{y}" width="{tile}" height="{tile}" rx="16" fill="{col}" opacity="0"><animate attributeName="opacity" values="0;.22;0" begin="{begin:.2f}s;{begin + 12:.2f}s" dur="1.4s"/></rect>'
                     f'{glyph}</g>' + text(x + tile / 2, y + tile + 20, label, 12, op=.75, anchor='middle'))
            x += tile + gap + 22
        y += tile + 56
    H = y + 10
    return svg(W, H, frame(W, H) + body, 'The stack: TypeScript, JavaScript, Python, Swift, Bash, HTML, CSS; Node.js, Three.js, Vite, PostgreSQL, Zod, MCP; Docker, Cloudflare, Vercel, Fly.io, GitHub Actions; Blender, Claude, passkeys.')


# ---------------------------------------------------------------- stats (live, with the wolf eating the graph)
Q = '''query($login:String!){user(login:$login){followers{totalCount}
contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{contributionCount date}}}}
repositories(ownerAffiliations:OWNER,isFork:false,first:100,privacy:PUBLIC){totalCount nodes{stargazerCount forkCount languages(first:10,orderBy:{field:SIZE,direction:DESC}){edges{size node{name color}}}}}}}'''


def fetch_stats():
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    payload = json.dumps({'query': Q, 'variables': {'login': USER}}).encode()
    try:
        if token:
            req = urllib.request.Request('https://api.github.com/graphql', payload, {'Authorization': f'bearer {token}', 'Content-Type': 'application/json'})
            data = json.load(urllib.request.urlopen(req, timeout=30))
        else:
            out = subprocess.run(['gh', 'api', 'graphql', '-f', f'query={Q}', '-F', f'login={USER}'], capture_output=True, text=True, timeout=60)
            data = json.loads(out.stdout)
        return data['data']['user']
    except Exception as e:  # keep yesterday's card rather than failing the build
        print('stats: unavailable', e)
        return None


def stats():
    u = fetch_stats()
    if not u:
        return None
    cal = u['contributionsCollection']['contributionCalendar']
    weeks = cal['weeks'][-52:]
    repos = u['repositories']
    stars_n = sum(r['stargazerCount'] for r in repos['nodes'])
    langs = {}
    for r in repos['nodes']:
        for e in r['languages']['edges']:
            n = e['node']['name']; langs.setdefault(n, [0, e['node']['color'] or '#888'])[0] += e['size']
    tot = sum(v[0] for v in langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1][0])[:6]
    W, H = 1280, 380
    body = frame(W, H)
    days = [d for w in weeks for d in w['contributionDays']]
    best = max(days, key=lambda d: d['contributionCount'])
    streak = run_ = 0
    for d in days:
        run_ = run_ + 1 if d['contributionCount'] else 0; streak = max(streak, run_)
    active = sum(1 for d in days if d['contributionCount'])
    nums = [(f"{cal['totalContributions']:,}", 'CONTRIBUTIONS, LAST YEAR', GREEN), (str(best['contributionCount']), f"BEST DAY · {dt.date.fromisoformat(best['date']).strftime('%d %b').upper()}", CYAN),
            (f'{streak} days', 'LONGEST STREAK', YELLOW), (str(active), 'DAYS SHIPPED', PINK)]
    for i, (v, l, c) in enumerate(nums):
        y = 70 + i * 74
        body += text(40, y + 6, v, 40, c, font=SANS, weight=900) + text(42, y + 30, l, 11, op=.5, ls=3)
    # the grid
    gx, gy, cs = 300, 50, 16
    mx = max([d['contributionCount'] for w in weeks for d in w['contributionDays']] + [1])
    pal = ['#15121f', '#0f3d2a', '#167a4a', '#22b866', GREEN]
    run = 12.0
    for wi, w in enumerate(weeks):
        for d in w['contributionDays']:
            di = dt.date.fromisoformat(d['date']).weekday()
            di = (di + 1) % 7
            c = d['contributionCount']
            lvl = 0 if c == 0 else 1 + min(3, int(3.999 * c / mx))
            x, y = gx + wi * (cs + 2), gy + di * (cs + 2)
            t = run * wi / len(weeks)
            if lvl:
                body += (f'<rect x="{x}" y="{y}" width="{cs}" height="{cs}" rx="3" fill="{pal[lvl]}">'
                         f'<animate attributeName="fill" values="{pal[lvl]};{pal[lvl]};{YELLOW};#15121f;#15121f;{pal[lvl]}" keyTimes="0;{t / run:.3f};{min(.999, t / run + .01):.3f};{min(.999, t / run + .04):.3f};.97;1" dur="{run}s" repeatCount="indefinite"/></rect>')
            else:
                body += f'<rect x="{x}" y="{y}" width="{cs}" height="{cs}" rx="3" fill="{pal[0]}"/>'
    gw = len(weeks) * (cs + 2)
    ww, wh = size_of('wolf-cheese')
    sc = 74 / wh
    body += (f'<g><image href="{cast("wolf-cheese")}" x="{gx - 40}" y="{gy + 7 * (cs + 2) - 64}" width="{ww * sc:.0f}" height="74" filter="url(#shadow)"/>'
             f'<animateTransform attributeName="transform" type="translate" values="0 0;{gw} 0;{gw} 0" keyTimes="0;.97;1" dur="{run}s" repeatCount="indefinite"/></g>')
    body += text(gx, gy + 7 * (cs + 2) + 34, 'the wolf eats one year of commits every 12 seconds. it grows back.', 12, op=.45)
    # languages bar
    by = 290
    body += text(gx, by - 12, 'LANGUAGES ACROSS PUBLIC REPOS', 11, op=.5, ls=3)
    x = gx
    for name, (size, col) in top:
        w = (W - 40 - gx) * size / sum(v[0] for _, v in top)
        body += f'<rect x="{x:.1f}" y="{by}" width="{max(w - 2, 1):.1f}" height="12" rx="3" fill="{col}"/>'
        x += w
    x = gx
    for name, (size, col) in top:
        lab = f'{name} {100 * size / tot:.0f}%'
        body += f'<circle cx="{x + 5}" cy="{by + 36}" r="5" fill="{col}"/>' + text(x + 16, by + 41, lab, 12, op=.8)
        x += 30 + len(lab) * 7.6
    body += text(W - 40, H - 18, f'live · updated {TODAY.strftime("%d %b %Y")}', 11, op=.3, anchor='end', ls=2)
    return svg(W, H, body, f"Live stats: {cal['totalContributions']} contributions in the last year, {repos['totalCount']} public repos, {stars_n} stars.")


# ---------------------------------------------------------------- terminal
TERM = [('$ whoami', GREEN), ('the architect · co-founder, Deimos AI LLC', '#fff'),
        ('$ deimos ls --built', GREEN), ('clockford  (patent pending)   ratchet   crimp  (patent pending)   marklode   m.a.x', '#fff'),
        ('$ deimos badges', GREEN), ('OpenSSF Best Practices: SILVER × 2   ·   clockford private beta: 10 NOV', YELLOW),
        ('$ sleep 8h', GREEN), ('sleep: refused. the agents never sleep either.', PINK),
        ('$ wolf --where', GREEN), ('🐺 somewhere on this page. he moves every day.', CYAN)]


def terminal():
    W, H = 1000, 400
    rows, t = '', 0.4
    for i, (s, col) in enumerate(TERM):
        y = 82 + i * 30
        typing = s.startswith('$')
        d = 0.05 * len(s) if typing else 0.05
        rows += (f'<clipPath id="c{i}"><rect x="28" y="{y - 22}" height="30" width="0"><animate attributeName="width" from="0" to="{W}" begin="{t:.2f}s" dur="{d:.2f}s" fill="freeze"/></rect></clipPath>'
                 + text(34, y, s, 17, col, extra=f'clip-path="url(#c{i})" xml:space="preserve"'))
        t += d + (0.25 if typing else 0.7)
    cy = 82 + len(TERM) * 30
    body = (f'<rect width="{W}" height="{H}" rx="16" fill="#0b0a12" stroke="#fff" stroke-opacity=".12"/>'
            f'<rect width="{W}" height="40" rx="16" fill="#16141f"/><rect y="24" width="{W}" height="16" fill="#16141f"/>'
            '<circle cx="26" cy="20" r="7" fill="#ff5f57"/><circle cx="50" cy="20" r="7" fill="#febc2e"/><circle cx="74" cy="20" r="7" fill="#28c840"/>'
            + text(W / 2, 25, 'architect@deimos: ~', 13, op=.5, anchor='middle') + rows
            + f'<rect x="34" y="{cy - 17}" width="10" height="20" fill="{GREEN}" opacity="0"><animate attributeName="opacity" values="1;0" dur=".9s" begin="{t:.1f}s" calcMode="discrete" repeatCount="indefinite"/></rect>')
    return svg(W, H, body, 'A terminal: whoami, the five builds, the badges, and a refusal to sleep.')


# ---------------------------------------------------------------- how I see it
def how():
    rng = random.Random(3)
    W, H = 1280, 470
    nodes = [(rng.uniform(70, 520), rng.uniform(70, 400)) for _ in range(22)]
    edges = set()
    for i, (x, y) in enumerate(nodes):
        near = sorted(range(len(nodes)), key=lambda j: (nodes[j][0] - x) ** 2 + (nodes[j][1] - y) ** 2)[1:3]
        for j in near: edges.add(tuple(sorted((i, j))))
    edges = sorted(edges)
    weak = set(rng.sample(range(len(edges)), 4))
    cyc = 10
    g = ''
    for k, (i, j) in enumerate(edges):
        (x1, y1), (x2, y2) = nodes[i], nodes[j]
        t = 1.2 + k * 2.4 / len(edges)
        L = math.hypot(x2 - x1, y2 - y1)
        col = PINK if k in weak else CYAN
        g += (f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{col}" stroke-width="{2.2 if k in weak else 1.5}" stroke-dasharray="{L:.0f}" stroke-dashoffset="{L:.0f}">'
              f'<animate attributeName="stroke-dashoffset" values="{L:.0f};{L:.0f};0;0;{L:.0f}" keyTimes="0;{t / cyc:.3f};{(t + .5) / cyc:.3f};.94;1" dur="{cyc}s" repeatCount="indefinite"/>'
              + (f'<animate attributeName="stroke" values="{PINK};{PINK};{GOLD};{GOLD}" keyTimes="0;.62;.66;1" dur="{cyc}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="stroke-opacity" values="1;.2;1;.2;1;1" keyTimes="0;.45;.5;.55;.6;1" dur="{cyc}s" repeatCount="indefinite"/>' if k in weak
                 else f'<animate attributeName="stroke" values="{CYAN};{CYAN};{GOLD};{GOLD}" keyTimes="0;.62;.66;1" dur="{cyc}s" repeatCount="indefinite"/>')
              + '</line>')
    for k, (x, y) in enumerate(nodes):
        t = k * 1.1 / len(nodes)
        g += (f'<circle cx="{x:.0f}" cy="{y:.0f}" r="5" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;{t / cyc:.3f};{(t + .2) / cyc:.3f};.94;1" dur="{cyc}s" repeatCount="indefinite"/>'
              f'<animate attributeName="fill" values="#ffffff;#ffffff;{GOLD};{GOLD}" keyTimes="0;.62;.66;1" dur="{cyc}s" repeatCount="indefinite"/></circle>')
    caption = (text(70, 440, 'see it', 12, CYAN, .8, ls=3) + text(160, 440, 'find where it breaks', 12, PINK, .8, ls=3) + text(380, 440, 'the pattern clicks', 12, GOLD, .8, ls=3))
    para = ['When I look at a problem, I see the whole', 'system laid out in front of me, lit up', 'like a map: every connection, every place', 'it could break. It feels like magic.',
            'Then I sit with the hunch until the pattern', 'clicks, and attack my own ideas harder than', 'anyone else will.']
    right = text(620, 78, 'HOW I SEE IT', 13, op=.5, ls=6) + ''.join(text(620, 116 + i * 28, l, 19, op=.92, font=SANS) for i, l in enumerate(para))
    rules = [('PEOPLE STAY IN CHARGE', GOLD), ('ASSUME SOMETHING IS INSIDE', PINK), ('MAKE IT PROVABLE', CYAN), ('BEND, DON’T BREAK', GREEN)]
    x, y = 620, 330
    for i, (r, c) in enumerate(rules):
        w = 26 + len(r) * 8.6
        if x + w > W - 40: x, y = 620, y + 50
        right += (f'<rect x="{x}" y="{y}" width="{w:.0f}" height="36" rx="18" fill="{c}" fill-opacity=".08" stroke="{c}" stroke-opacity=".7">'
                  f'<animate attributeName="fill-opacity" values=".08;.3;.08" begin="{i * 1.5}s" dur="3s" repeatCount="indefinite"/></rect>'
                  + text(x + w / 2, y + 23, r, 12, c, anchor='middle', ls=1.5, weight=700))
        x += w + 12
    body = frame(W, H) + f'<rect x="30" y="30" width="530" height="410" rx="16" fill="{PANEL}"/>' + g + caption + right
    return svg(W, H, body, 'How I see it: the whole system laid out like a map; find where it breaks; the pattern clicks. Four rules.')


# ---------------------------------------------------------------- the cast
def cast_scene():
    rng = random.Random(9)
    W, H = 1280, 560
    rw, rh = size_of('rook'); s = 400 / rh; rw2 = rw * s
    ww, wh = size_of('wolf-cheese'); s2 = 250 / wh; ww2 = ww * s2
    rx, wx = 300, 840
    floor = 500
    lines = [('rook', 'Every agent in town, accounted for.'), ('wolf', '…and every crumb of cheese.'),
             ('rook', 'Beta opens 10 November.'), ('wolf', 'bring cheese.')]
    bub = ''
    n = len(lines); cyc = 16
    for i, (who, s_) in enumerate(lines):
        bw = 30 + len(s_) * 10.2
        bx = rx + rw2 / 2 - 30 if who == 'rook' else wx + ww2 / 2 - bw + 40
        by = 70 if who == 'rook' else 200
        a, b = i / n, (i + 1) / n
        col = '#ffffff' if who == 'rook' else YELLOW
        tail = (f'<path d="M{bx + 40},{by + 44} l-6,22 l24,-22z" fill="{col}"/>' if who == 'rook' else f'<path d="M{bx + bw - 60},{by + 44} l14,24 l6,-24z" fill="{col}"/>')
        bub += (f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{a:.3f};{a + .02:.3f};{b - .03:.3f};{b - .01:.3f};1" dur="{cyc}s" repeatCount="indefinite"/>'
                f'<rect x="{bx:.0f}" y="{by}" width="{bw:.0f}" height="46" rx="23" fill="{col}"/>{tail}' + text(bx + bw / 2, by + 30, s_, 17, BG, anchor='middle', weight=700) + '</g>')
    defs = (f'<radialGradient id="spot1" cx=".5" cy="0" r="1"><stop offset="0" stop-color="{CYAN}" stop-opacity=".35"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>'
            f'<radialGradient id="spot2" cx=".5" cy="0" r="1"><stop offset="0" stop-color="{YELLOW}" stop-opacity=".3"/><stop offset="1" stop-color="{YELLOW}" stop-opacity="0"/></radialGradient>'
            f'<radialGradient id="pool"><stop offset="0" stop-color="#fff" stop-opacity=".16"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".25"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<mask id="refl"><rect x="0" y="{floor}" width="{W}" height="60" fill="url(#fade)"/></mask>'
            f'<clipPath id="stage"><rect width="{W}" height="{H}" rx="22"/></clipPath>')
    figs = (f'<image href="{cast("rook")}" x="{rx}" y="{floor - 400}" width="{rw2:.0f}" height="400" filter="url(#shadow)"/>'
            f'<image href="{cast("wolf-cheese")}" x="{wx}" y="{floor - 250}" width="{ww2:.0f}" height="250" filter="url(#shadow)"/>')
    refl = (f'<g mask="url(#refl)" opacity=".5"><g transform="translate(0 {2 * floor}) scale(1 -1)">'
            f'<image href="{cast("rook")}" x="{rx}" y="{floor - 400}" width="{rw2:.0f}" height="400"/><image href="{cast("wolf-cheese")}" x="{wx}" y="{floor - 250}" width="{ww2:.0f}" height="250"/></g></g>')
    body = (f'<g clip-path="url(#stage)"><rect width="{W}" height="{H}" fill="{BG}"/>{stars(W, H, 60, rng)}'
            f'<polygon points="{rx + rw2 / 2 - 60},0 {rx + rw2 / 2 + 60},0 {rx + rw2 / 2 + 240},{floor} {rx + rw2 / 2 - 240},{floor}" fill="url(#spot1)"/>'
            f'<polygon points="{wx + ww2 / 2 - 50},0 {wx + ww2 / 2 + 50},0 {wx + ww2 / 2 + 190},{floor} {wx + ww2 / 2 - 190},{floor}" fill="url(#spot2)"/>'
            f'<rect x="0" y="{floor}" width="{W}" height="{H - floor}" fill="#0a0812"/><line x1="0" y1="{floor}" x2="{W}" y2="{floor}" stroke="#fff" stroke-opacity=".1"/>'
            f'<ellipse cx="{rx + rw2 / 2}" cy="{floor + 4}" rx="190" ry="22" fill="url(#pool)"/><ellipse cx="{wx + ww2 / 2}" cy="{floor + 4}" rx="150" ry="18" fill="url(#pool)"/>'
            f'{refl}{figs}{bub}'
            + text(60, 64, 'THE CAST', 13, op=.5, ls=6)
            + text(rx + rw2 / 2, floor + 40, 'ROOK · lives in Clockford', 13, CYAN, .85, anchor='middle', ls=2)
            + text(wx + ww2 / 2, floor + 40, 'THE WOLF · head of security (self-appointed)', 13, YELLOW, .85, anchor='middle', ls=2)
            + '</g>' + f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="none" stroke="#fff" stroke-opacity=".1"/>')
    return svg(W, H, body, 'The cast: Rook, who lives in Clockford, and the wolf, head of security (self-appointed), trading lines on a dark stage.', defs)


# ---------------------------------------------------------------- timeline
def timeline():
    W, H = 1280, 250
    pts = [('2022', 'CO-PRODUCER', 'Gaming Wall St · HBO Max', '#fff'), ('2026', 'OPENSSF SILVER × 2', 'Ratchet + Crimp', GREEN),
           ('2026', 'PATENTS PENDING', 'Clockford + Crimp', GOLD), ('10 NOV 2026', 'PRIVATE BETA', 'Clockford opens its doors', PINK)]
    x0, x1, y = 120, 1160, 120
    body = frame(W, H) + text(40, 46, 'THE ROAD SO FAR', 13, op=.5, ls=6)
    body += f'<line x1="{x0}" y1="{y}" x2="{x1 - 180}" y2="{y}" stroke="#fff" stroke-opacity=".3" stroke-width="2"/><line x1="{x1 - 180}" y1="{y}" x2="{x1}" y2="{y}" stroke="{PINK}" stroke-opacity=".6" stroke-width="2" stroke-dasharray="6 6"/>'
    body += f'<circle r="5" fill="#fff" filter="url(#glow)"><animateMotion path="M{x0},{y} L{x1},{y}" dur="6s" repeatCount="indefinite"/></circle>'
    for i, (when, what, sub, col) in enumerate(pts):
        x = x0 + i * (x1 - x0) / (len(pts) - 1)
        pulse = i == len(pts) - 1
        body += (f'<circle cx="{x:.0f}" cy="{y}" r="10" fill="{BG}" stroke="{col}" stroke-width="3"/>'
                 + (f'<circle cx="{x:.0f}" cy="{y}" r="10" fill="none" stroke="{col}" stroke-width="2"><animate attributeName="r" values="10;30" dur="2s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;0" dur="2s" repeatCount="indefinite"/></circle>' if pulse else '')
                 + text(x, y - 26, when, 13, col, .9, anchor='middle', ls=3)
                 + text(x, y + 44, what, 16, col, anchor='middle', font=SANS, weight=900, ls=1.5)
                 + text(x, y + 66, sub, 13, op=.6, anchor='middle'))
    return svg(W, H, body, 'The road so far: 2022 co-producer (HBO Max); 2026 OpenSSF Silver for Ratchet and Crimp; patents pending; 10 November 2026 Clockford private beta.')


# ---------------------------------------------------------------- the wall, wide
def wall():
    W, H = 1280, 640
    img = uri(A / 'cast' / 'wall-scene.webp')
    iw, ih = 1002, 1360
    sh = H; sw = iw * sh / ih   # ~471
    sx = (W - sw) / 2 + 140
    defs = (f'<linearGradient id="lf" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".22" stop-color="#fff"/><stop offset=".78" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<mask id="m"><rect x="{sx}" y="0" width="{sw}" height="{H}" fill="url(#lf)"/></mask>'
            f'<filter id="amb" x="0" y="0" width="100%" height="100%"><feGaussianBlur stdDeviation="40"/><feColorMatrix type="matrix" values=".55 0 0 0 0  0 .5 0 0 0  0 0 .45 0 0  0 0 0 1 0"/></filter>'
            f'<clipPath id="cl"><rect width="{W}" height="{H}" rx="22"/></clipPath>'
            f'<linearGradient id="vg" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="{BG}" stop-opacity=".6"/><stop offset=".25" stop-color="{BG}" stop-opacity="0"/><stop offset=".8" stop-color="{BG}" stop-opacity="0"/><stop offset="1" stop-color="{BG}" stop-opacity=".9"/></linearGradient>')
    body = (f'<g clip-path="url(#cl)"><rect width="{W}" height="{H}" fill="{BG}"/>'
            f'<image href="{uri(A / "cast" / "wall-ambient.webp")}" x="-80" y="-140" width="{W + 160}" height="{H + 280}" preserveAspectRatio="xMidYMid slice" filter="url(#amb)" opacity=".75"/>'
            f'<rect width="{W}" height="{H}" fill="{BG}" opacity=".35"/>'
            f'<image href="{img}" x="{sx:.0f}" y="0" width="{sw:.0f}" height="{sh}" mask="url(#m)"/>'
            f'<rect width="{W}" height="{H}" fill="url(#vg)"/>'
            + text(70, 250, 'THE WOLF', 64, '#fff', font=SANS, weight=900, ls=4)
            + text(70, 320, 'FOUND', 64, '#fff', font=SANS, weight=900, ls=4)
            + text(70, 390, 'THE WALL.', 64, YELLOW, font=SANS, weight=900, ls=4)
            + text(74, 440, 'every system has one. he always finds it.', 16, op=.65)
            + deimos(1150, 520, .2, '#fff', '#fff') + text(1150, 590, 'DEIMOS AI LLC', 11, op=.6, anchor='middle', ls=4)
            + '</g>' + f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="none" stroke="#fff" stroke-opacity=".1"/>')
    return svg(W, H, body, 'The wolf found the wall: a wolf pup with cheese looks up at the Deimos mark sprayed on a concrete wall.', defs)


# ---------------------------------------------------------------- dividers (the wolf of the day lives in one of them)
WOLF_LINES = ['you found the wolf. tell no one.', 'the wolf was here. the cheese was not.', 'cheese tax collected. carry on.',
              'he moves every day. come back tomorrow.', 'unpaid intern. paid in cheese.', 'head of security (self-appointed).',
              'he read your agent logs. he has notes.', 'zero trust. some cheese.']


def poses():
    return sorted(p.stem for p in (A / 'cast').glob('wolf-*.webp'))  # every cut-out pose; wall-* are scenery


def divider(k, wolf_here):
    W, H = 1280, 120
    col = [CYAN, PINK, GOLD][k % 3]
    body = (f'<line x1="40" y1="60" x2="{W - 40}" y2="60" stroke="{col}" stroke-opacity=".25"/>'
            f'<circle r="4" fill="{col}" filter="url(#glow)"><animateMotion path="M40,60 L{W - 40},60" dur="{5 + k}s" repeatCount="indefinite"/></circle>')
    if wolf_here:
        pose = day_rng.choice(poses())
        line = day_rng.choice(WOLF_LINES)
        pw, ph = size_of(pose); hh = 112; w = pw * hh / ph
        x = day_rng.randint(120, W - 520)
        body += (f'<rect x="{x + w + 4}" y="44" width="{28 + len(line) * 9.1:.0f}" height="32" rx="16" fill="{BG}" stroke="{YELLOW}" stroke-opacity=".5"/>'
                 f'<image href="{cast(pose)}" x="{x}" y="{H - hh - 2}" width="{w:.0f}" height="{hh}" filter="url(#shadow)"/>'
                 + text(x + w + 18, 66, line, 15, YELLOW, .9, extra='font-style="italic"'))
    return svg(W, H, body, 'The wolf of the day.' if wolf_here else 'divider')


def main():
    A.mkdir(exist_ok=True)
    out = {'hero.svg': hero(), 'now.svg': now(), 'systems.svg': systems(), 'stack.svg': stack(), 'terminal.svg': terminal(),
           'how.svg': how(), 'cast.svg': cast_scene(), 'timeline.svg': timeline(), 'wall.svg': wall()}
    for i in range(len(CARDS)):
        out[f'card-{CARDS[i][0].lower().replace(".", "")}.svg'] = card(i)
    pick = day_rng.randrange(3)
    for k in range(3):
        out[f'divider-{k + 1}.svg'] = divider(k, k == pick)
    st = stats()
    if st: out['stats.svg'] = st
    for name, s in out.items():
        (A / name).write_text(s, encoding='utf-8')
        print(f'{name:22} {len(s) // 1024:5d} KB')


if __name__ == '__main__':
    main()
