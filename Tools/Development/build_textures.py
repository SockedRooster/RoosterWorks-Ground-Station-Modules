"""Build the Ground Modules dev.40 texture pass from the approved dev.39 install."""
from pathlib import Path
from types import SimpleNamespace, FunctionType
import io
import json
import os
import sys
import zipfile
import numpy as np

ROOT = Path(__file__).resolve().parent
SDK = next((ROOT.parent / "Releases/2026-11-02").glob("*Modules*Source"))
sys.path[:0] = [str(SDK / ".build-deps"), str(SDK / "Source")]
from PIL import Image, ImageDraw, ImageFilter
import appearance_textures as artwork

SIZE = 2048
PREFIX = "GameData/RoosterWorksGroundModules/"


class PanelCanvas:
    """Render the existing panel drawings in their original 1024-unit coordinate space."""
    def __init__(self, mode, size, color):
        self.image = Image.new(mode, tuple(2 * x for x in size), color)
        self.draw = ImageDraw.Draw(self.image)

    def paste(self, tile, position):
        self.image.paste(tile.image, tuple(2 * x for x in position))

    def primitive(self, name, xy, **style):
        for key in ("width", "radius"):
            if key in style:
                style[key] *= 2
        getattr(self.draw, name)(tuple(2 * x for x in xy), **style)

    def text(self, xy, value, **style):
        self.draw.text(tuple(2 * x for x in xy), value, **style)

    def __getattr__(self, name):
        if name in ("rectangle", "rounded_rectangle", "line", "ellipse"):
            return lambda xy, **kw: self.primitive(name, xy, **kw)
        raise AttributeError(name)


def panel(fn, *args):
    context = dict(fn.__globals__, Image=SimpleNamespace(new=PanelCanvas),
                   ImageDraw=SimpleNamespace(Draw=lambda canvas: canvas),
                   font=lambda size, bold=False: artwork.font(2 * size, bold))
    return FunctionType(fn.__code__, context)(*args).image


def field(seed):
    rng = np.random.default_rng(seed)
    result = np.zeros((SIZE, SIZE), dtype=np.float32)
    for grid, weight in ((10, 1), (23, .48), (49, .23), (113, .08)):
        src = Image.fromarray(rng.integers(0, 256, (grid, grid), dtype=np.uint8))
        smooth = src.resize((SIZE, SIZE), Image.Resampling.BICUBIC)
        smooth = smooth.filter(ImageFilter.GaussianBlur(SIZE / grid * .08))
        result += (np.asarray(smooth, dtype=np.float32) / 255 - .5) * weight
    return result


def blanket_images():
    grain, fine = field(811), field(519)
    axis = np.arange(SIZE, dtype=np.float32) / SIZE
    x, y = axis[None, :], axis[:, None]
    edge = np.minimum(np.minimum(x, 1-x), np.minimum(y, 1-y))
    rim = np.exp(-((edge-.037)/.005)**2)
    seam = np.exp(-((edge-.053)/.0028)**2)
    wrinkle = .30*grain + .055*np.sin(x*180+grain*17)*np.sin(y*124+fine*13)
    weave = 1.1*np.sin(2*np.pi*(x*317 + fine*.4))*np.sin(2*np.pi*(y*281 + grain*.5))
    shade = grain*12 - rim*7 + seam*5 + wrinkle*9 + weave
    for name, base in (("cladding", (204,207,199)), ("cladding_white", (223,225,216))):
        rgb = np.uint8(np.clip(np.asarray(base, np.float32) + shade[:,:,None], 0, 255))
        im = Image.fromarray(rgb)
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((166,1602,770,1768), radius=16, fill=tuple(int(v*.92) for v in base),
                            outline=tuple(int(v*.68) for v in base), width=4)
        ink = tuple(int(v*.42) for v in base)
        d.text((196,1632), "RW  /  MLI-07", font=artwork.font(46,True), fill=ink)
        d.text((196,1702), "THERMAL COVER", font=artwork.font(28), fill=ink)
        for px in (96,1952):
            for py in (96,1952):
                d.ellipse((px-18,py-18,px+18,py+18), fill=(109,119,117), outline=(221,224,211), width=4)
                d.line((px-8,py,px+8,py), fill=(49,59,60), width=4)
        im.putalpha(Image.fromarray(np.uint8(np.clip(38+grain*12+rim*22,20,80))))
        yield name, im
    folds = grain*39 + fine*10 + 1.8*np.sin(x*308 + fine*21)*np.sin(y*227 + grain*15)
    colors = np.array([169,130,64]) + folds[:,:,None]*np.asarray([1,.85,.5])
    im = Image.fromarray(np.uint8(np.clip(colors,0,255)))
    im.putalpha(Image.fromarray(np.uint8(np.clip(155+grain*45,90,190))))
    yield "hubblanket", im


def build():
    base = next(ROOT.glob("*dev.39-Install.zip"))
    target = base.with_name(base.name.replace("dev.39","dev.40"))
    updated = dict(blanket_images())
    updated["detail"] = panel(artwork.atlas)
    for name in ("instrument","display","logpanel"):
        updated[name] = panel(artwork.grille, name)
    pending = target.with_suffix(".partial")
    with zipfile.ZipFile(base) as old, zipfile.ZipFile(pending,"w") as out:
        for info in old.infolist():
            data = old.read(info)
            name = Path(info.filename).stem.removeprefix("rwm_")
            if info.filename == PREFIX+"Models/rwm_"+name+".png" and name in updated:
                buf = io.BytesIO()
                updated[name].save(buf, format="PNG")
                data = buf.getvalue()
            elif info.filename.endswith(".version"):
                meta = json.loads(data)
                meta["VERSION"]["BUILD"] = 40
                data = (json.dumps(meta,indent=2)+"\n").encode()
            out.writestr(info,data)
    with zipfile.ZipFile(base) as old, zipfile.ZipFile(pending) as new:
        assert new.testzip() is None and new.namelist()==old.namelist()
        changed = {n for n in new.namelist() if old.read(n)!=new.read(n)}
        assert changed == {PREFIX+"Models/rwm_"+n+".png" for n in updated} | {PREFIX+"RoosterWorksGroundModules.version"}
        for n in new.namelist():
            if n.endswith(".png"):
                with Image.open(io.BytesIO(new.read(n))) as im:
                    im.load()
                    if n in changed:
                        prior = Image.open(io.BytesIO(old.read(n)))
                        assert im.size==(SIZE,SIZE) and im.mode==prior.mode
                        assert np.abs(np.asarray(im.resize(prior.size),dtype=float)-np.asarray(prior)).mean()<5, n
    os.replace(pending,target)
    print(target, len(updated), "textures rebuilt")


if __name__=="__main__":
    build()
