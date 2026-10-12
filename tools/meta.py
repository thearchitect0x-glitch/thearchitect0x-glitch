# Where each cut-out's feet are, so every character stands on the same floor: assets/cast/meta.json (needs Pillow).
import json, pathlib
from PIL import Image
D = pathlib.Path(__file__).resolve().parent.parent / 'assets' / 'cast'
meta = {}
for p in sorted(D.glob('*.webp')):
    if p.stem.startswith('wall'): continue
    im = Image.open(p).convert('RGBA'); a = im.getchannel('A'); w, h = im.size
    px = a.load()
    rows = [y for y in range(h) if sum(1 for x in range(0, w, 2) if px[x, y] > 200) >= max(3, w // 40)]
    foot = rows[-1] if rows else h - 1
    cols = [x for x in range(w) if any(px[x, y] > 200 for y in range(max(0, foot - 12), foot + 1))]
    meta[p.stem] = {'w': w, 'h': h, 'foot': foot, 'fx0': min(cols) if cols else 0, 'fx1': max(cols) if cols else w}
json.dump(meta, open(D / 'meta.json', 'w'), indent=1)
print(json.dumps(meta)[:600])

# Rook's chest screen, so the countdown sits exactly on it (needs numpy + opencv)
try:
    import numpy as np, cv2
    im = np.array(Image.open(D / 'rook.webp').convert('RGBA')); H, W_ = im.shape[:2]
    hsv = cv2.cvtColor(np.ascontiguousarray(im[:, :, :3]), cv2.COLOR_RGB2HSV)
    m = ((hsv[:, :, 2] > 200) & (hsv[:, :, 1] < 40)).astype(np.uint8); m[:int(H * .45)] = 0; m[int(H * .8):] = 0
    k, lab, st, _ = cv2.connectedComponentsWithStats(m, 8); i = 1 + int(np.argmax(st[1:, 4]))
    x, y, w, h = (int(v) for v in st[i][:4])
    meta['rook']['screen'] = [x + 3, y + 3, w - 6, h - 6]
    json.dump(meta, open(D / 'meta.json', 'w'), indent=1)
    print('screen', meta['rook']['screen'])
except ImportError:
    pass
