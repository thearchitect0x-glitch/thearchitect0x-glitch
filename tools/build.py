# Builds the animated SVGs for the GitHub profile: hero.svg, systems.svg, terminal.svg.
# Pure SVG + SMIL (GitHub renders these inside <img>; no scripts, no web fonts, images embedded as data URIs).
import base64, math, pathlib, random

ROOT = pathlib.Path(__file__).resolve().parent.parent
A = ROOT / 'assets'
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
SANS = "'Helvetica Neue',Helvetica,Arial,sans-serif"
rnd = random.Random(11)


def uri(name, mime=None):
    p = A / name
    mime = mime or {'jpg': 'image/jpeg', 'png': 'image/png', 'svg': 'image/svg+xml'}[p.suffix[1:]]
    return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"


def deimos(cx, cy, s, color='#fff', node='#fff'):
    """The Deimos mark (circle, tetrahedron seen from above, core) at scale s around (cx, cy)."""
    R = 154 * s
    v = [(cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))) for a in (-90, 150, 30)]
    tri = ' '.join(f'{x:.1f},{y:.1f}' for x, y in v)
    spokes = ''.join(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}"/>' for x, y in v)
    nodes = ''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{19 * s:.1f}"/>' for x, y in v)
    return (f'<g fill="none" stroke="{color}" stroke-linejoin="round">'
            f'<circle cx="{cx}" cy="{cy}" r="{R:.1f}" stroke-width="{8 * s:.1f}" stroke-opacity=".8"/>'
            f'<polygon points="{tri}" stroke-width="{7 * s:.1f}"/><g stroke-width="{6 * s:.1f}">{spokes}</g></g>'
            f'<g fill="{node}">{nodes}<circle cx="{cx}" cy="{cy}" r="{26.5 * s:.1f}"/></g>')


def gear(cx, cy, r, teeth, color, dur, rev=False):
    pts = []
    for i in range(teeth * 4):
        a = 2 * math.pi * i / (teeth * 4)
        rr = r if i % 4 in (0, 1) else r * 0.82
        pts.append(f'{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}')
    to = '-360' if rev else '360'
    return (f'<g><polygon points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="2.2"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r * .35:.1f}" fill="none" stroke="{color}" stroke-width="2"/>'
            f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="{to} {cx} {cy}" dur="{dur}s" repeatCount="indefinite"/></g>')


ACID = ['#ff2bd6', '#7a5cff', '#00e5ff', '#39ff88', '#fff23a', '#ff7a1a', '#ff2bd6']


def cycle(attr, off=0, dur=9):
    vals = ';'.join(ACID[off:] + ACID[1:off + 1]) if off else ';'.join(ACID)
    return f'<animate attributeName="{attr}" values="{vals}" dur="{dur}s" repeatCount="indefinite"/>'


def mandala(cx, cy, n, r0, r1, w, dur, rev, grad):
    petal = (f'M0,{-r0} C{w},{-(r0 + r1) / 2} {w},{-(r0 + r1) / 2 - 10} 0,{-r1} '
             f'C{-w},{-(r0 + r1) / 2 - 10} {-w},{-(r0 + r1) / 2} 0,{-r0}Z')
    ps = ''.join(f'<path d="{petal}" transform="rotate({360 * i / n})"/>' for i in range(n))
    to = -360 if rev else 360
    return (f'<g transform="translate({cx} {cy})"><g fill="url(#{grad})" fill-opacity=".55" stroke="#fff" stroke-opacity=".18">{ps}'
            f'<animateTransform attributeName="transform" type="rotate" from="0" to="{to}" dur="{dur}s" repeatCount="indefinite"/></g></g>')


def hero():
    W, H = 1280, 460
    cx, cy = 300, 230
    blobs = ''
    for i, (x, y, r) in enumerate([(160, 120, 210), (420, 340, 230), (760, 110, 200), (1080, 330, 240), (620, 420, 180)]):
        dx, dy = rnd.randint(-90, 90), rnd.randint(-60, 60)
        blobs += (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{ACID[i]}">{cycle("fill", i + 1, 11 + i * 2)}'
                  f'<animateTransform attributeName="transform" type="translate" values="0 0;{dx} {dy};0 0" dur="{13 + i * 3}s" repeatCount="indefinite"/></circle>')
    orbits = ''
    for k, rot in enumerate((0, 60, 120)):
        path = f'M{cx - 200},{cy} a200,62 0 1,0 400,0 a200,62 0 1,0 -400,0'
        orbits += (f'<g transform="rotate({rot} {cx} {cy})"><path id="orb{k}" d="{path}" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="2" stroke-dasharray="2 7"/>'
                   f'<circle r="7" fill="#fff"><animateMotion dur="{4 + k * 1.3}s" repeatCount="indefinite"><mpath href="#orb{k}"/></animateMotion></circle></g>')
    ticks = ''.join(f'<line x1="{cx}" y1="{cy - 222}" x2="{cx}" y2="{cy - (204 if i % 5 else 194)}" transform="rotate({i * 6} {cx} {cy})"/>' for i in range(60))
    title = 'THE ARCHITECT'
    glitch = lambda col, xs: (f'<text x="600" y="205" fill="{col}" opacity=".85" font-family="{SANS}" font-size="66" font-weight="900" letter-spacing="3">{title}'
                              f'<animate attributeName="x" values="{xs}" dur="2.6s" calcMode="discrete" repeatCount="indefinite"/></text>')
    wolf = uri('wolf-shades.jpg')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="The Architect: co-founder, Deimos AI LLC. Builder of Clockford, Ratchet, Crimp, Marklode and M.A.X.">
<defs>
<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="55"/></filter>
<filter id="hue"><feColorMatrix type="hueRotate" values="0"><animate attributeName="values" values="0;360" dur="14s" repeatCount="indefinite"/></feColorMatrix></filter>
<filter id="glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<radialGradient id="pet"><stop offset="0" stop-color="#fff">{cycle("stop-color", 2, 7)}</stop><stop offset="1" stop-color="#ff2bd6">{cycle("stop-color", 4, 7)}</stop></radialGradient>
<radialGradient id="pet2"><stop offset="0" stop-color="#00e5ff">{cycle("stop-color", 3, 5)}</stop><stop offset="1" stop-color="#7a5cff" stop-opacity=".2">{cycle("stop-color", 5, 5)}</stop></radialGradient>
<linearGradient id="tg" x1="0" x2="1"><stop offset="0" stop-color="#fff23a">{cycle("stop-color", 1, 6)}</stop><stop offset=".5" stop-color="#fff"/><stop offset="1" stop-color="#00e5ff">{cycle("stop-color", 4, 6)}</stop></linearGradient>
<clipPath id="type"><rect x="600" y="296" width="0" height="30"><animate attributeName="width" values="0;480;480;480;0" keyTimes="0;.25;.4;.9;1" dur="11s" repeatCount="indefinite"/></rect></clipPath>
<clipPath id="type2"><rect x="600" y="327" width="0" height="30"><animate attributeName="width" values="0;0;320;320;0" keyTimes="0;.28;.42;.9;1" dur="11s" repeatCount="indefinite"/></rect></clipPath>
<clipPath id="wc"><circle cx="1185" cy="530" r="64"/></clipPath>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".22"/></pattern>
</defs>
<rect width="{W}" height="{H}" rx="22" fill="#05040a"/>
<g filter="url(#hue)">
<g filter="url(#blur)" opacity=".42">{blobs}</g>
{mandala(cx, cy, 12, 40, 190, 46, 48, False, "pet")}
{mandala(cx, cy, 24, 120, 236, 22, 70, True, "pet2")}
<g stroke="#fff" stroke-opacity=".7" stroke-width="2">{ticks}<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="60s" repeatCount="indefinite"/></g>
{gear(92, 392, 34, 12, "#fff", 9)}{gear(146, 404, 22, 8, "#fff", 6, True)}{gear(1230, 60, 26, 10, "#fff", 8)}
</g>
<g filter="url(#glow)">{orbits}{deimos(cx, cy, .62)}</g>
{glitch("#00e5ff", "597;600;603;596;600;600;601")}{glitch("#ff2bd6", "603;600;597;604;600;600;599")}
<text x="600" y="205" fill="url(#tg)" font-family="{SANS}" font-size="66" font-weight="900" letter-spacing="3">{title}</text>
<text x="604" y="252" fill="#fff" fill-opacity=".85" font-family="{MONO}" font-size="21" letter-spacing="3">CO-FOUNDER · DEIMOS AI LLC</text>
<g clip-path="url(#type)"><text x="604" y="318" fill="#39ff88" font-family="{MONO}" font-size="19">&gt; I see systems laid out in front of me.</text></g>
<g clip-path="url(#type2)"><text x="604" y="348" fill="#39ff88" font-family="{MONO}" font-size="19">&gt; Then I build the answer.</text></g>
<rect x="604" y="358" width="11" height="18" fill="#39ff88"><animate attributeName="opacity" values="1;0" dur=".8s" calcMode="discrete" repeatCount="indefinite"/></rect>
<text x="604" y="410" fill="#fff" fill-opacity=".7" font-family="{MONO}" font-size="15" letter-spacing="4">CLOCKFORD · RATCHET · CRIMP · MARKLODE · M.A.X</text>
<rect width="{W}" height="{H}" rx="22" fill="url(#scan)"/>
<g><animateTransform attributeName="transform" type="translate" values="0 0;0 0;0 -150;0 -150;0 0;0 0" keyTimes="0;.55;.6;.82;.87;1" dur="15s" repeatCount="indefinite"/>
<circle cx="1185" cy="530" r="68" fill="#fff23a"/>
<image href="{wolf}" x="1121" y="466" width="128" height="128" clip-path="url(#wc)"/>
<text x="1000" y="482" fill="#fff23a" font-family="{MONO}" font-size="16">psst. 🧀</text></g>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="none" stroke="#fff" stroke-opacity=".12"/>
</svg>'''


PRODUCTS = [
    ('CLOCKFORD', '#F7CD45', 'see · approve · stop your AI agents from your phone', 'patent pending', (300, 130)),
    ('RATCHET', '#39ff88', 'every real-world effect, at most once', 'OpenSSF Silver', (980, 130)),
    ('CRIMP', '#ff2bd6', 'decisions that withdraw themselves when a fact breaks', 'patent pending · OpenSSF Silver', (990, 420)),
    ('MARKLODE', '#00e5ff', 'diligence before the pitch, in 24 to 72 hours', 'marklode.com', (290, 420)),
    ('M.A.X', '#ff7a1a', 'behavior, read against each person’s own baseline', 'deimoscore.com', (640, 520)),
]


def systems():
    W, H = 1280, 680
    cx, cy = 640, 300
    rules = 'PEOPLE STAY IN CHARGE OF WHAT MATTERS  ✦  ASSUME SOMETHING IS ALREADY INSIDE  ✦  IF IT MATTERS, MAKE IT PROVABLE  ✦  BEND, DON’T BREAK  ✦  '
    rings = ''
    for i, r in enumerate((150, 215, 280)):
        rings += (f'<ellipse cx="{cx}" cy="{cy}" rx="{r * 1.9:.0f}" ry="{r * .95:.0f}" fill="none" stroke="#fff" stroke-opacity="{.10 + .05 * i:.2f}" stroke-width="1.5" stroke-dasharray="3 9">'
                  f'<animate attributeName="stroke-dashoffset" values="0;{120 if i % 2 else -120}" dur="{6 + i * 2}s" repeatCount="indefinite"/></ellipse>')
    planets = ''
    cm = uri('clockford-mark.svg')
    for k, (name, col, line, tag, ang) in enumerate(PRODUCTS):
        px, py = ang
        tx, anchor = px, 'middle'
        inner = (f'<image href="{cm}" x="{px - 26:.0f}" y="{py - 26:.0f}" width="52" height="52" clip-path="url(#cmc)"/>' if name == 'CLOCKFORD'
                 else f'<text x="{px:.0f}" y="{py + 8:.0f}" text-anchor="middle" fill="#05040a" font-family="{SANS}" font-weight="900" font-size="22">{name[0]}</text>')
        planets += f'''<path id="beam{k}" d="M{cx},{cy} L{px:.1f},{py:.1f}" stroke="{col}" stroke-opacity=".35" stroke-width="1.5"/>
<circle r="4.5" fill="{col}"><animateMotion dur="{1.8 + k * .35:.2f}s" repeatCount="indefinite" begin="{k * .4:.1f}s"><mpath href="#beam{k}"/></animateMotion></circle>
<circle cx="{px:.1f}" cy="{py:.1f}" r="40" fill="{col}" opacity=".25" filter="url(#g2)"><animate attributeName="r" values="34;48;34" dur="{2.5 + k * .4:.1f}s" repeatCount="indefinite"/></circle>
<circle cx="{px:.1f}" cy="{py:.1f}" r="30" fill="{col}"/>
{inner.replace('clip-path="url(#cmc)"', f'clip-path="url(#cmc{k})"')}
<clipPath id="cmc{k}"><circle cx="{px:.1f}" cy="{py:.1f}" r="26"/></clipPath>
<text x="{tx:.0f}" y="{py + 66:.0f}" text-anchor="{anchor}" fill="{col}" font-family="{SANS}" font-weight="900" font-size="24" letter-spacing="3">{name}</text>
<text x="{tx:.0f}" y="{py + 88:.0f}" text-anchor="{anchor}" fill="#fff" fill-opacity=".88" font-family="{MONO}" font-size="14">{line}</text>
<text x="{tx:.0f}" y="{py + 107:.0f}" text-anchor="{anchor}" fill="#fff" fill-opacity=".5" font-family="{MONO}" font-size="12" letter-spacing="2">{tag.upper()}</text>'''
    rp = f'M{cx - 618},{cy + 40} a618,318 0 1,1 1236,0 a618,318 0 1,1 -1236,0'
    stars = ''.join(f'<circle cx="{rnd.randint(0, W)}" cy="{rnd.randint(0, H)}" r="{rnd.choice((.8, 1.1, 1.6))}" fill="#fff"><animate attributeName="opacity" values=".1;.9;.1" dur="{rnd.uniform(2, 6):.1f}s" begin="{rnd.uniform(0, 4):.1f}s" repeatCount="indefinite"/></circle>' for _ in range(90))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="The system map: Deimos at the core; Clockford, Ratchet, Crimp, Marklode and M.A.X in orbit; four rules around the edge.">
<defs>
<filter id="g2" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="14"/></filter>
<filter id="hue"><feColorMatrix type="hueRotate" values="0"><animate attributeName="values" values="0;360" dur="20s" repeatCount="indefinite"/></feColorMatrix></filter>
<radialGradient id="neb"><stop offset="0" stop-color="#7a5cff" stop-opacity=".55"/><stop offset=".5" stop-color="#ff2bd6" stop-opacity=".18"/><stop offset="1" stop-color="#05040a" stop-opacity="0"/></radialGradient>
<path id="rules" d="{rp}"/>
</defs>
<rect width="{W}" height="{H}" rx="22" fill="#05040a"/>
{stars}
<g filter="url(#hue)"><ellipse cx="{cx}" cy="{cy}" rx="560" ry="300" fill="url(#neb)"/>{rings}</g>
<text font-family="{MONO}" font-size="13" letter-spacing="4" fill="#fff" fill-opacity=".45"><textPath href="#rules" startOffset="0">{rules * 3}<animate attributeName="startOffset" values="0;-2900" dur="60s" repeatCount="indefinite"/></textPath></text>
{planets}
<circle cx="{cx}" cy="{cy}" r="78" fill="#05040a" stroke="#fff" stroke-opacity=".2"/>
<g filter="url(#hue)"><circle cx="{cx}" cy="{cy}" r="92" fill="none" stroke="#ff2bd6" stroke-width="2" stroke-dasharray="1 11"><animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="18s" repeatCount="indefinite"/></circle></g>
{deimos(cx, cy, .42)}
<text x="{cx}" y="{cy + 118}" text-anchor="middle" fill="#fff" fill-opacity=".8" font-family="{MONO}" font-size="13" letter-spacing="6">DEIMOS AI</text>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="none" stroke="#fff" stroke-opacity=".12"/>
</svg>'''


TERM = [
    ('$ whoami', '#39ff88'),
    ('the architect · co-founder, Deimos AI LLC', '#fff'),
    ('$ deimos ls --built', '#39ff88'),
    ('clockford  (patent pending)   ratchet   crimp  (patent pending)   marklode   m.a.x', '#fff'),
    ('$ deimos badges', '#39ff88'),
    ('OpenSSF Best Practices: SILVER × 2   ·   clockford private beta: 10 NOV', '#fff23a'),
    ('$ sleep 8h', '#39ff88'),
    ('sleep: refused. the agents never sleep either.', '#ff2bd6'),
    ('$ wolf --where', '#39ff88'),
    ('🐺 somewhere on this page. he moves every day.', '#00e5ff'),
]


def terminal():
    W, H = 1000, 400
    rows, t = '', 0.4
    for i, (txt, col) in enumerate(TERM):
        y = 82 + i * 30
        typing = txt.startswith('$')
        d = 0.05 * len(txt) if typing else 0.05
        cid = f'c{i}'
        rows += (f'<clipPath id="{cid}"><rect x="28" y="{y - 22}" height="30" width="0"><animate attributeName="width" from="0" to="{W}" begin="{t:.2f}s" dur="{d:.2f}s" fill="freeze"/></rect></clipPath>'
                 f'<text x="34" y="{y}" fill="{col}" font-family="{MONO}" font-size="17" clip-path="url(#{cid})" xml:space="preserve">{txt}</text>')
        t += d + (0.25 if typing else 0.7)
    cy = 82 + len(TERM) * 30
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="A terminal: whoami, the five builds, the badges, and a refusal to sleep.">
<rect width="{W}" height="{H}" rx="16" fill="#0b0a12" stroke="#fff" stroke-opacity=".12"/>
<rect width="{W}" height="40" rx="16" fill="#16141f"/><rect y="24" width="{W}" height="16" fill="#16141f"/>
<circle cx="26" cy="20" r="7" fill="#ff5f57"/><circle cx="50" cy="20" r="7" fill="#febc2e"/><circle cx="74" cy="20" r="7" fill="#28c840"/>
<text x="{W / 2}" y="25" text-anchor="middle" fill="#fff" fill-opacity=".5" font-family="{MONO}" font-size="13">architect@deimos: ~</text>
{rows}
<rect x="34" y="{cy - 17}" width="10" height="20" fill="#39ff88" opacity="0"><animate attributeName="opacity" values="1;0" dur=".9s" begin="{t:.1f}s" calcMode="discrete" repeatCount="indefinite"/></rect>
</svg>'''


if __name__ == '__main__':
    for name, fn in (('hero.svg', hero), ('systems.svg', systems), ('terminal.svg', terminal)):
        (A / name).write_text(fn(), encoding='utf-8')
        print(name, (A / name).stat().st_size)
