# Repaint the wolf graffiti: remove the old atom mark (and the viewer's "AI-Generated" chip), spray the new Deimos mark.
import sys, numpy as np, cv2
src, out = sys.argv[1], sys.argv[2]
rng = np.random.default_rng(7)
im = cv2.imread(src); H, W = im.shape[:2]
L = cv2.cvtColor(im, cv2.COLOR_BGR2LAB)[:, :, 0].astype(np.float32)
yy, xx = np.mgrid[0:H, 0:W]
wolf = ((xx - 515) / 150.0) ** 2 + ((yy - 1160) / 255.0) ** 2 < 1
wolf |= (yy > 1150) & (xx > 330) & (xx < 700)
# the wall without paint: a grey closing wider than any stroke or blob, then smoothed
k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (161, 161))
bg = cv2.GaussianBlur(cv2.morphologyEx(cv2.resize(L, (W // 2, H // 2)), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (81, 81))), (0, 0), 15)
bg = cv2.resize(bg, (W, H))
box = (((xx - 512) / 395.0) ** 2 + ((yy - 560) / 480.0) ** 2 < 1)
mask = box & (L < bg - 16) & ~wolf
mask |= (xx > 760) & (yy < 90)
mask = cv2.dilate(mask.astype(np.uint8), np.ones((13, 13), np.uint8)) > 0
mask &= ~wolf
# low frequencies: inpaint at small scale
s = 4
small = cv2.resize(im, (W // s, H // s), interpolation=cv2.INTER_AREA)
msmall = cv2.resize(mask.astype(np.uint8) * 255, (W // s, H // s), interpolation=cv2.INTER_NEAREST)
msmall = cv2.dilate(msmall, np.ones((5, 5), np.uint8))
low = cv2.resize(cv2.inpaint(small, msmall, 9, cv2.INPAINT_TELEA), (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32)
low = cv2.GaussianBlur(low, (0, 0), 6)
low_inp = low.copy()
# lighting: a smooth cubic surface fitted to the clean wall around the mark, so the patch matches the room's light
fb = cv2.GaussianBlur(im.astype(np.float32), (0, 0), 9)
ring = (xx > 40) & (xx < 990) & (yy > 60) & (yy < 1100) & ~cv2.dilate(mask.astype(np.uint8), np.ones((25, 25), np.uint8)).astype(bool) & ~wolf
sel = np.nonzero(ring[::6, ::6]); py, px = sel[0] * 6, sel[1] * 6
def basis(x, y):
    x = x / W - .5; y = y / H - .5
    return np.stack([x**i * y**j for i in range(4) for j in range(4 - i)], -1)
A = basis(px.astype(np.float32), py.astype(np.float32))
G = basis(xx.astype(np.float32), yy.astype(np.float32))
low = np.stack([G @ np.linalg.lstsq(A, fb[py, px, c], rcond=None)[0] for c in range(3)], -1).astype(np.float32)
wb = cv2.GaussianBlur(box.astype(np.float32), (0, 0), 25)[:, :, None]
low = low * wb + low_inp * (1 - wb)
# high frequencies: quilt from clean wall blocks in the same height band
f = im.astype(np.float32); hp = f - cv2.GaussianBlur(f, (0, 0), 6)
clean = ~cv2.dilate(mask.astype(np.uint8), np.ones((31, 31), np.uint8)).astype(bool) & ~wolf
tex = np.zeros_like(f); wsum = np.zeros((H, W, 1), np.float32)
B, step = 72, 48
win = np.outer(np.hanning(B), np.hanning(B)).astype(np.float32)[:, :, None] + 1e-3
for y0 in range(0, H - B + 1 + step, step):
    y0 = min(y0, H - B)
    for x0 in range(0, W - B + 1 + step, step):
        x0 = min(x0, W - B)
        if not mask[y0:y0 + B, x0:x0 + B].any(): continue
        for _ in range(400):
            sy = int(np.clip(y0 + rng.integers(-60, 61), 0, H - B)); sx = int(rng.integers(0, W - B))
            if clean[sy:sy + B, sx:sx + B].all(): break
        tex[y0:y0 + B, x0:x0 + B] += hp[sy:sy + B, sx:sx + B] * win; wsum[y0:y0 + B, x0:x0 + B] += win
tex = tex / np.maximum(wsum, 1e-3)
fill = low + tex
m = cv2.GaussianBlur(mask.astype(np.float32), (0, 0), 3)[:, :, None]
wall = f * (1 - m) + fill * m
# the new mark, sprayed
cx, cy, R = 512, 470, 300
paint = np.zeros((H, W), np.float32)
ang = np.radians([-90, 150, 30]); V = [(int(cx + R * np.cos(a)), int(cy + R * np.sin(a))) for a in ang]
cv2.circle(paint, (cx, cy), R, 1.0, 20, cv2.LINE_AA)
cv2.polylines(paint, [np.array(V, np.int32)], True, 1.0, 19, cv2.LINE_AA)
for v in V: cv2.line(paint, (cx, cy), v, 1.0, 14, cv2.LINE_AA)
for v in V: cv2.circle(paint, v, 34, 1.0, -1, cv2.LINE_AA)
cv2.circle(paint, (cx, cy), 50, 1.0, -1, cv2.LINE_AA)
core = cv2.GaussianBlur(paint, (0, 0), 1.6)
over = cv2.GaussianBlur(paint, (0, 0), 11) * 0.35
spk = (rng.random((H, W)) < 0.05).astype(np.float32) * (cv2.GaussianBlur(paint, (0, 0), 22) > 0.06)
alpha = np.clip(np.maximum(core, over) + spk * 0.5, 0, 1)
# drips from the low edges of strokes
drips = np.zeros((H, W), np.float32)
ys, xs = np.nonzero(paint > 0.5)
for _ in range(46):
    i = rng.integers(len(xs)); x, y = int(xs[i]), int(ys[i])
    col = np.nonzero(paint[:, x] > 0.5)[0]; y = int(col[col >= y].max()) if len(col) else y
    ln = int(rng.choice([rng.integers(25, 90), rng.integers(90, 260), rng.integers(260, 470)], p=[.5, .35, .15]))
    w = float(rng.uniform(3, 7.5)); wob = rng.uniform(-1.5, 1.5)
    for t in range(ln):
        k = 1 - 0.55 * t / ln
        cv2.circle(drips, (int(x + wob * np.sin(t / 40)), y + t), max(1, int(w * k / 2 + .5)), 1.0, -1, cv2.LINE_AA)
    cv2.circle(drips, (int(x + wob * np.sin(ln / 40)), y + ln), int(w * .75), 1.0, -1, cv2.LINE_AA)
alpha = np.maximum(alpha, cv2.GaussianBlur(drips, (0, 0), 1.1))
alpha *= (0.86 + 0.14 * cv2.GaussianBlur(rng.random((H, W)).astype(np.float32), (0, 0), 1.5))
alpha[wolf] = 0
a = cv2.GaussianBlur(alpha, (0, 0), 0.6)[:, :, None]
ink = np.array([22, 21, 20], np.float32)
res = wall * (1 - a * 0.94) + ink * a * 0.94
cv2.imwrite(out, np.clip(res, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])
