# Clean the wall: remove the old atom mark (and the viewer's chip), leaving bare concrete, the wolf and the floor.
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
cv2.imwrite(out, np.clip(wall, 0, 255).astype(np.uint8))
