# Cut-outs → small WebP with alpha for embedding in the SVGs. Run when a new pose is added (needs Pillow).
import sys, pathlib
from PIL import Image, ImageFilter
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / 'assets' / 'cast'; OUT.mkdir(parents=True, exist_ok=True)
def prep(src, name, h):
    im = Image.open(src).convert('RGBA'); im = im.crop(im.getbbox())
    a = im.getchannel('A').filter(ImageFilter.MinFilter(3))       # trim the light fringe from the matte
    im.putalpha(a.filter(ImageFilter.GaussianBlur(0.6)))
    im = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
    im.save(OUT / f'{name}.webp', 'WEBP', quality=86, method=6)
    print(name, im.size, (OUT / f'{name}.webp').stat().st_size)
cuts = ROOT / 'src'
prep(cuts / 'cut-robot.webp', 'robot', 440)                       # copy the robot's cut-out here first
prep(cuts / 'cut-w5.png', 'wolf-back', 300)
prep(cuts / 'cut-w6.png', 'wolf-cheesehat', 300)
prep(cuts / 'cut-w7.png', 'wolf-cheese', 300)
for p in sorted((ROOT / 'wolves').glob('*')) if (ROOT / 'wolves').exists() else []:
    if p.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp'): prep(p, 'wolf-' + p.stem.lower(), 300)
