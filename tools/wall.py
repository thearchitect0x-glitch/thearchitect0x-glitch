# The wolf found the wall, wide: clean leftovers, widen the room both ways, and spray the Deimos mark like real paint.
import sys, numpy as np, cv2
src, out = sys.argv[1], sys.argv[2]
EXT = int(sys.argv[3]) if len(sys.argv) > 3 else 760
rng = np.random.default_rng(23)
im = cv2.imread(src).astype(np.float32); H, W = im.shape[:2]
yy, xx = np.mgrid[0:H, 0:W]
L = cv2.cvtColor(im.astype(np.uint8), cv2.COLOR_BGR2LAB)[:, :, 0].astype(np.float32)
wolf = ((xx - 515) / 150.0) ** 2 + ((yy - 1160) / 255.0) ** 2 < 1
wolf |= (yy > 1150) & (xx > 330) & (xx < 700)
# 1. leftover drip stubs near the wolf's ears and on the left
bg = cv2.GaussianBlur(cv2.morphologyEx(L, cv2.MORPH_CLOSE, np.ones((41, 41), np.uint8)), (0, 0), 8)
stub = (((yy > 860) & (yy < 1030) & (xx > 260) & (xx < 720)) & (L < bg - 22) & ~wolf).astype(np.uint8)
stub = cv2.morphologyEx(stub, cv2.MORPH_OPEN, np.ones((9, 1), np.uint8))
stub = cv2.dilate(stub, np.ones((5, 5), np.uint8)) & (~wolf).astype(np.uint8)
im = cv2.inpaint(im.astype(np.uint8), stub, 3, cv2.INPAINT_TELEA).astype(np.float32)
W2 = W + 2 * EXT
if EXT == 0:
    res = im.copy()
else:
# 2. widen (unused when EXT=0): per-row light continues outward and dims (a vignette), concrete grain quilted from bare areas of the same height
  W2 = W + 2 * EXT
  big = np.zeros((H, W2, 3), np.float32); big[:, EXT:EXT + W] = im
  edgeL = cv2.GaussianBlur(im[:, 8:70].mean(1, keepdims=True), (0, 0), 12)[:, 0]
  edgeR = cv2.GaussianBlur(im[:, W - 70:W - 8].mean(1, keepdims=True), (0, 0), 12)[:, 0]
  d = np.arange(EXT, dtype=np.float32)
  fall = (0.62 + 0.38 * np.exp(-d / 900.0))[None, :, None]   # dimmer away from the light
  big[:, :EXT] = edgeL[:, None, :] * fall[:, ::-1]
  big[:, EXT + W:] = edgeR[:, None, :] * fall
  lowpass = cv2.GaussianBlur(im, (0, 0), 6); hp = im - lowpass
  crumbs = (cv2.cvtColor(im.astype(np.uint8), cv2.COLOR_BGR2HSV)[:, :, 1] > 110)
  cleansrc = ~(cv2.dilate((wolf | crumbs).astype(np.uint8), np.ones((41, 41), np.uint8)).astype(bool))
  cleansrc[:, 180:850] &= ~((np.arange(H) > 1150) & (np.arange(H) < 1300))[:, None]   # the spray cans
  B, step = 96, 64
  win = np.outer(np.hanning(B), np.hanning(B)).astype(np.float32)[:, :, None] + 1e-3
  tex = np.zeros_like(big); ws = np.zeros((H, W2, 1), np.float32)
  for y0 in list(range(0, H - B, step)) + [H - B]:
      for x0 in list(range(0, W2 - B, step)) + [W2 - B]:
          if EXT + 40 <= x0 and x0 + B <= EXT + W - 40: continue
          for _ in range(300):
              sy = int(np.clip(y0 + rng.integers(-24, 25), 0, H - B)); sx = int(rng.integers(0, W - B))
              if cleansrc[sy:sy + B, sx:sx + B].all(): break
          tex[y0:y0 + B, x0:x0 + B] += hp[sy:sy + B, sx:sx + B] * win; ws[y0:y0 + B, x0:x0 + B] += win
  tex /= np.maximum(ws, 1e-3)
  low = cv2.GaussianBlur(big, (0, 0), 3)
  syn = low + tex
  # blend the real image in over a soft seam
  ramp = np.zeros(W2, np.float32); ramp[EXT:EXT + W] = 1
  ramp = cv2.GaussianBlur(ramp[None, :], (0, 0), 30)[0]; ramp[EXT + 60:EXT + W - 60] = 1
  big[:, EXT:EXT + W] = im
  res = syn * (1 - ramp[None, :, None]) + big * ramp[None, :, None]
  # carry the wall's vertical panel seams outward: two more seams each side, as faint dark lines with grain
  for x in (EXT - 330, EXT - 690, EXT + W + 330, EXT + W + 690):
      if 0 < x < W2:
          seam = np.zeros((H, W2), np.float32); cv2.line(seam, (x, 0), (x + int(rng.integers(-3, 4)), 1185), 1.0, 2, cv2.LINE_AA)
          seam = cv2.GaussianBlur(seam, (0, 0), 1.2) * (0.6 + 0.4 * rng.random((H, W2)).astype(np.float32))
          res *= (1 - 0.22 * seam)[:, :, None]
# overall vignette so the wide frame reads as one shot
vx = (np.arange(W2) - W2 / 2) / (W2 / 2); vy = (np.arange(H) - H * 0.45) / H
vig = 1 - 0.28 * np.clip(vx[None, :] ** 2 * 0.9 + vy[:, None] ** 2 * 0.6, 0, 1)
res *= vig[:, :, None]
# 3. the mark, sprayed: hand wobble, uneven pressure, paint soaking into the grain, overspray, a few honest drips
cx, cy, R = EXT + 512, 470, 300
Y2, X2 = np.mgrid[0:H, 0:W2]
def stroke_mask():
    m = np.zeros((H, W2), np.float32)
    ang = np.radians([-90, 150, 30]); V = [(cx + R * np.cos(a), cy + R * np.sin(a)) for a in ang]
    sc = 4  # draw at 4x for smooth sub-pixel wobble, then shrink
    big4 = np.zeros((H, W2), np.float32)
    def P(p): return (int(p[0] * 16), int(p[1] * 16))
    cv2.circle(big4, P((cx, cy)), R * 16, 1.0, 21, cv2.LINE_AA, 4)
    cv2.polylines(big4, [np.array([[int(v[0] * 16), int(v[1] * 16)] for v in V], np.int32)], True, 1.0, 19, cv2.LINE_AA, 4)
    for v in V: cv2.line(big4, P((cx, cy)), P(v), 1.0, 15, cv2.LINE_AA, 4)
    for v in V: cv2.circle(big4, P(v), 33 * 16, 1.0, -1, cv2.LINE_AA, 4)
    cv2.circle(big4, P((cx, cy)), 49 * 16, 1.0, -1, cv2.LINE_AA, 4)
    return big4, V
paint, V = stroke_mask()
# hand wobble: warp the mark with slow noise (a few px)
def noise(scale, amp):
    n = cv2.resize(rng.standard_normal((H // scale + 2, W2 // scale + 2)).astype(np.float32), (W2, H), interpolation=cv2.INTER_CUBIC)
    return n * amp
mx = (X2 + noise(90, 2.6)).astype(np.float32); my = (Y2 + noise(90, 2.6)).astype(np.float32)
paint = cv2.remap(paint, mx, my, cv2.INTER_LINEAR)
core = cv2.GaussianBlur(paint, (0, 0), 1.3)
soft = cv2.GaussianBlur(paint, (0, 0), 5.0)
over = cv2.GaussianBlur(paint, (0, 0), 16) * 0.22
pressure = np.clip(0.80 + noise(140, 0.10) + noise(25, 0.05), 0.55, 1.0)
alpha = np.maximum(np.maximum(core, soft * 0.85) * pressure, over)
# overspray dots: denser near strokes, varied size
halo = cv2.GaussianBlur(paint, (0, 0), 20)
dots = np.zeros((H, W2), np.float32)
ys, xs = np.nonzero((halo > 0.03) & (paint < 0.2))
pick = rng.choice(len(xs), size=min(len(xs), 5200), replace=False)
for i in pick:
    if rng.random() < halo[ys[i], xs[i]] * 1.7:
        cv2.circle(dots, (int(xs[i]), int(ys[i])), int(rng.choice([0, 0, 0, 1, 1, 2])), float(rng.uniform(.25, .7)), -1, cv2.LINE_AA)
alpha = np.maximum(alpha, cv2.GaussianBlur(dots, (0, 0), .6))
# drips: only where paint pooled (node bottoms, lowest arc, under the bar), varied
drips = np.zeros((H, W2), np.float32)
starts = [(V[1][0] + dx, V[1][1] + 30) for dx in (-14, 9)] + [(V[2][0] + dx, V[2][1] + 30) for dx in (-6, 16)] + [(cx + dx, cy + 46) for dx in (-20, 12)]
starts += [(cx + R * np.cos(a), cy + R * np.sin(a) + 9) for a in np.radians(rng.uniform(55, 125, 9))]
starts += [(x, V[1][1] + 9) for x in rng.uniform(V[1][0] + 60, V[2][0] - 60, 6)]
for (x, y) in starts:
    ln = int(rng.choice([rng.integers(18, 60), rng.integers(60, 180), rng.integers(180, 330)], p=[.45, .4, .15]))
    w = float(rng.uniform(2.4, 5.5)); drift = rng.uniform(-.04, .04)
    for t in range(ln):
        k = 1 - 0.5 * t / ln
        cv2.circle(drips, (int(x + drift * t), int(y + t)), max(1, int(w * k / 2 + .5)), float(.9 - .25 * t / ln), -1, cv2.LINE_AA)
    cv2.ellipse(drips, (int(x + drift * ln), int(y + ln)), (int(w * .7) + 1, int(w * .95) + 1), 0, 0, 360, .85, -1, cv2.LINE_AA)
alpha = np.maximum(alpha, cv2.GaussianBlur(drips, (0, 0), .9))
# soak into the concrete: pores take more paint, high spots less
lum = cv2.cvtColor(np.clip(res, 0, 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)
grain = (lum - cv2.GaussianBlur(lum, (0, 0), 3)) / 18.0
alpha = np.clip(alpha * (1 - 0.22 * np.tanh(grain)), 0, 1)
# never over the wolf
wolf2 = np.zeros((H, W2), bool); wolf2[:, EXT:EXT + W] = wolf
alpha[wolf2] = 0
a = alpha[:, :, None]
# matte black paint multiplies the wall's own light (so it sits IN the scene), with a faint sheen where it's thick
ink = np.array([0.10, 0.10, 0.11], np.float32)
res = res * (1 - a) + res * ink * a
sheen = cv2.GaussianBlur(paint, (0, 0), 2) * np.clip(noise(30, .5) + .2, 0, 1) * 6
res += sheen[:, :, None] * (vig[:, :, None] * 0.6)
# 4. crop to the scene and a little film grain to unify
y0, y1 = 70, 1480
res = res[y0:y1]
res += rng.normal(0, 3.2, res.shape).astype(np.float32)
cv2.imwrite(out, np.clip(res, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 90])
print(res.shape)
