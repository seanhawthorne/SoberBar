#!/usr/bin/env python3
"""
Sober Bar - Dubai Chocolatte
Renders a 1080x1920 / 30fps frame sequence for TikTok.

Camera moves are computed in float and resampled with Lanczos so the motion is
genuinely smooth instead of the stair-stepping you get from ffmpeg zoompan.
"""
import math
import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
KIT = HERE.parent
SOURCE = KIT / "source"
FRAMES = HERE / "frames"
FONTS = HERE / "fonts"

W, H = 1080, 1920
FPS = 30
AR = W / H  # 0.5625

IMG_HERO = SOURCE / "hero-side.png"   # side hero, 1254px
IMG_TOP = SOURCE / "top-down.jpeg"    # top-down, 4032px
LOGO = KIT.parents[2] / "public" / "logo-white.png"

CREAM = (244, 234, 216)
GOLD = (212, 175, 106)
LIGHT_GOLD = (238, 217, 164)

F_SANS = str(FONTS / "JosefinSans%5Bwght%5D.ttf")
F_SERIF = str(FONTS / "CormorantGaramond%5Bwght%5D.ttf")


# ---------------------------------------------------------------- easing ----
def clamp01(t):
    return max(0.0, min(1.0, t))


def ease_out_cubic(t):
    return 1 - (1 - clamp01(t)) ** 3


def ease_out_quint(t):
    return 1 - (1 - clamp01(t)) ** 5


def ease_in_out_cubic(t):
    t = clamp01(t)
    return 4 * t**3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def lerp(a, b, t):
    return a + (b - a) * t


# ------------------------------------------------------------ font cache ----
_font_cache = {}


def font(path, size, weight=None):
    key = (path, size, weight)
    if key not in _font_cache:
        f = ImageFont.truetype(path, size)
        if weight is not None:
            try:
                f.set_variation_by_axes([weight])
            except Exception:
                pass
        _font_cache[key] = f
    return _font_cache[key]


# ------------------------------------------------------------- sources -----
def load_sources():
    """Pre-crop each source to its widest usable 9:16 window, capped in size so
    the per-frame Lanczos resample stays fast but still oversamples 1080px."""
    src = {}

    hero = Image.open(IMG_HERO).convert("RGB")
    # Hero: the glass sits right-of-centre. Frame the 9:16 window on it, keeping
    # the candle just inside the left edge.
    hw, hh = hero.size
    win_h = hh
    win_w = win_h * AR
    cx = hw * 0.585
    left = max(0, min(hw - win_w, cx - win_w / 2))
    hero = hero.crop((int(left), 0, int(left + win_w), hh))
    src["hero"] = hero

    top = Image.open(IMG_TOP).convert("RGB")
    tw, th = top.size
    win_h = th
    win_w = win_h * AR
    cx = tw * 0.480  # centre of the drink
    left = max(0, min(tw - win_w, cx - win_w / 2))
    top = top.crop((int(left), 0, int(left + win_w), th))
    # 4032px source is far more than we need; 2600 tall still oversamples 3x
    if top.height > 2600:
        top = top.resize((int(top.width * 2600 / top.height), 2600), Image.LANCZOS)
    src["top"] = top

    return src


# -------------------------------------------------------------- camera -----
def frame_from(img, cx, cy, zoom, rot=0.0, shake=(0.0, 0.0)):
    """Crop a 9:16 window at (cx,cy) normalised, scaled by `zoom`, -> 1080x1920."""
    iw, ih = img.size
    win_h = ih / zoom
    win_w = win_h * AR
    if win_w > iw:
        win_w = iw
        win_h = win_w / AR

    px = cx * iw + shake[0] * (win_w / W)
    py = cy * ih + shake[1] * (win_h / H)

    # keep the window inside the source
    px = max(win_w / 2, min(iw - win_w / 2, px))
    py = max(win_h / 2, min(ih - win_h / 2, py))

    box = (px - win_w / 2, py - win_h / 2, px + win_w / 2, py + win_h / 2)
    out = img.resize((W, H), Image.LANCZOS, box=box)

    if abs(rot) > 0.001:
        # rotate about centre then re-crop so no empty corners appear
        pad = 1.0 + abs(math.sin(math.radians(rot))) * 2.2
        big = img.resize((int(W * pad), int(H * pad)), Image.LANCZOS, box=box)
        big = big.rotate(rot, resample=Image.BICUBIC, expand=False)
        bw, bh = big.size
        out = big.crop(
            (
                int((bw - W) / 2),
                int((bh - H) / 2),
                int((bw - W) / 2) + W,
                int((bh - H) / 2) + H,
            )
        )
    return out


def handheld(t, amp=2.6):
    """Sub-pixel drift so a still photograph reads as a held camera."""
    x = amp * (math.sin(2 * math.pi * 0.31 * t + 1.1) + 0.45 * math.sin(2 * math.pi * 0.83 * t + 2.7))
    y = amp * (math.sin(2 * math.pi * 0.24 * t + 0.4) + 0.40 * math.sin(2 * math.pi * 0.67 * t + 5.1))
    return (x, y)


# --------------------------------------------------------------- grade -----
def grade(img, bloom=0.16, warmth=1.0):
    """Filmic contrast + a whisper of warm highlights / cool shadows + bloom.

    Deliberately restrained: the source photos are already very warm, and the
    pistachio has to stay readably *green* or the whole premise dies.
    """
    a = np.asarray(img).astype(np.float32) / 255.0

    # gentle S-curve
    a = np.clip(a, 0, 1)
    a = a * a * (3 - 2 * a) * 0.22 + a * 0.78

    lum = a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114
    hi = np.clip((lum - 0.68) / 0.32, 0, 1)[..., None]
    sh = np.clip((0.38 - lum) / 0.38, 0, 1)[..., None]

    # protect anything already green-dominant from the warm push
    green_bias = np.clip(
        (a[..., 1] - np.maximum(a[..., 0], a[..., 2])) * 6.0, 0, 1
    )[..., None]
    keep = 1.0 - 0.85 * green_bias

    warm = np.array([0.020, 0.007, -0.012], np.float32) * warmth
    cool = np.array([-0.012, -0.003, 0.020], np.float32) * warmth
    a = a + hi * warm * keep + sh * cool

    # a touch of saturation
    g = (a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114)[..., None]
    a = g + (a - g) * 1.05

    # lifted, slightly milky blacks
    a = a * (1.0 - 0.030) + 0.030 * np.array([0.055, 0.048, 0.052], np.float32)

    a = np.clip(a, 0, 1)
    out = Image.fromarray((a * 255).astype(np.uint8))

    if bloom > 0:
        hl = np.clip((np.asarray(out).astype(np.float32) / 255.0 - 0.68) / 0.32, 0, 1)
        hl_img = Image.fromarray((hl * 255).astype(np.uint8)).filter(
            ImageFilter.GaussianBlur(26)
        )
        b = np.asarray(hl_img).astype(np.float32) / 255.0
        base = np.asarray(out).astype(np.float32) / 255.0
        out = Image.fromarray(
            (np.clip(base + b * bloom, 0, 1) * 255).astype(np.uint8)
        )

    return out


def vignette_mask(strength=0.42):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    nx = (xx - W / 2) / (W / 2)
    ny = (yy - H / 2) / (H / 2)
    r = np.sqrt(nx * nx * 0.92 + ny * ny * 0.78)
    m = np.clip(1.0 - strength * np.clip((r - 0.42) / 0.85, 0, 1) ** 1.6, 0, 1)
    return m[..., None]


VIG = vignette_mask()


def apply_vignette(img):
    a = np.asarray(img).astype(np.float32) * VIG
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


# ---------------------------------------------------------------- text -----
def text_layer(draw_fn):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(layer), layer)
    return layer


def draw_tracked(draw, xy, text, fnt, fill, tracking=0.0, anchor="lt"):
    """Letter-spaced text. Returns the total advance width."""
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + tracking * max(0, len(text) - 1)
    x, y = xy
    if anchor[0] == "m":
        x -= total / 2
    elif anchor[0] == "r":
        x -= total
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill, anchor="l" + anchor[1])
        x += w + tracking
    return total


def shadowed(layer, blur=18, spread=1.9, opacity=190):
    """Soft dark halo behind a text layer so it survives a busy photo."""
    alpha = layer.split()[3]
    halo = alpha.filter(ImageFilter.MaxFilter(3))
    halo = halo.filter(ImageFilter.GaussianBlur(blur))
    halo = halo.point(lambda p: min(255, int(p * spread)))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow.putalpha(halo.point(lambda p: int(p * opacity / 255)))
    out = Image.alpha_composite(shadow, layer)
    return out


def scrim(height_frac=0.34, opacity=150, top=False):
    """Gradient scrim for lower-third legibility."""
    m = np.zeros((H, W), np.float32)
    hpx = int(H * height_frac)
    ramp = np.linspace(0, 1, hpx) ** 1.7
    if top:
        m[:hpx] = ramp[::-1][:, None]
    else:
        m[H - hpx :] = ramp[:, None]
    img = Image.new("RGBA", (W, H), (5, 4, 4, 0))
    img.putalpha(Image.fromarray((m * opacity).astype(np.uint8)))
    return img


SCRIM_BOTTOM = scrim(0.36, 165)
SCRIM_TOP = scrim(0.42, 175, top=True)


# ------------------------------------------------------------ animation ----
def anim_in(t, start, dur=0.36):
    """Returns (alpha 0..1, y-offset px) for a rise-and-fade-in."""
    p = ease_out_quint((t - start) / dur)
    return p, (1 - p) * 26


def band(t, start, end, fade_in=0.36, fade_out=0.22):
    """Opacity envelope for a text beat."""
    if t < start or t > end:
        return 0.0
    a = ease_out_quint((t - start) / fade_in)
    b = 1.0 - ease_in_out_cubic((t - (end - fade_out)) / fade_out) if t > end - fade_out else 1.0
    return max(0.0, min(a, b))


def fade_layer(layer, alpha, dy=0.0):
    if alpha <= 0.001:
        return None
    out = layer
    if abs(dy) > 0.4:
        out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        out.paste(layer, (0, int(round(dy))))
    if alpha < 0.999:
        a = out.split()[3].point(lambda p: int(p * alpha))
        out = out.copy()
        out.putalpha(a)
    return out


# ------------------------------------------------------------- copy -------
def build_text_layers():
    L = {}

    # -- 1. HOOK -------------------------------------------------------
    def hook(d, layer):
        f_kick = font(F_SERIF, 64, 600)
        f_big = font(F_SANS, 118, 700)
        y = int(H * 0.205)
        # cream, not gold: this beat plays over the brightest plate in the film
        draw_tracked(d, (W / 2, y), "DUBAI CHOCOLATE", f_kick, CREAM, tracking=9, anchor="mt")
        d.text((W / 2, y + 92), "BUT YOU", font=f_big, fill=CREAM, anchor="mt")
        d.text((W / 2, y + 92 + 118), "DRINK IT", font=f_big, fill=CREAM, anchor="mt")

    L["hook"] = shadowed(text_layer(hook), blur=22, opacity=205)

    # -- 2. SENSORY ----------------------------------------------------
    def sensory(d, layer):
        f = font(F_SANS, 76, 600)
        y = int(H * 0.245)
        d.text((W / 2, y), "pistachio on top.", font=f, fill=CREAM, anchor="mt")
        d.text((W / 2, y + 92), "chocolate all the", font=f, fill=CREAM, anchor="mt")
        d.text((W / 2, y + 184), "way down.", font=f, fill=CREAM, anchor="mt")

    L["sensory"] = shadowed(text_layer(sensory), blur=20, opacity=195)

    # -- 3. SETUP (curiosity gap across the cut) -----------------------
    def setup(d, layer):
        f = font(F_SERIF, 92, 600)
        d.text((W / 2, int(H * 0.245)), "and it is completely", font=f, fill=CREAM, anchor="mt")

    L["setup"] = shadowed(text_layer(setup), blur=24, spread=2.1, opacity=210)

    # -- 4. TWIST ------------------------------------------------------
    def twist(d, layer):
        f_num = font(F_SANS, 260, 700)
        f_sub = font(F_SANS, 84, 500)
        y = int(H * 0.29)
        d.text((W / 2, y), "0%", font=f_num, fill=CREAM, anchor="mt")
        draw_tracked(d, (W / 2, y + 274), "ALCOHOL", f_sub, CREAM, tracking=18, anchor="mt")

    L["twist"] = shadowed(text_layer(twist), blur=32, spread=2.4, opacity=225)

    # -- 4b. TWIST support --------------------------------------------
    def twist2(d, layer):
        f = font(F_SERIF, 70, 500)
        d.text((W / 2, int(H * 0.545)), "everything on our menu is.", font=f, fill=LIGHT_GOLD, anchor="mt")

    L["twist2"] = shadowed(text_layer(twist2), blur=20, opacity=200)

    # -- 5. CTA --------------------------------------------------------
    logo = Image.open(LOGO).convert("RGBA")
    bbox = logo.split()[3].getbbox()
    if bbox:
        logo = logo.crop(bbox)
    lw = int(W * 0.66)
    logo = logo.resize((lw, max(1, int(logo.height * lw / logo.width))), Image.LANCZOS)

    def cta(d, layer):
        ly = int(H * 0.415)
        layer.alpha_composite(logo, (int((W - logo.width) / 2), ly))
        f_city = font(F_SERIF, 66, 500)
        f_addr = font(F_SANS, 44, 400)
        base = ly + logo.height + 46
        draw_tracked(d, (W / 2, base), "GULFPORT · FLORIDA", f_city, GOLD, tracking=8, anchor="mt")
        draw_tracked(d, (W / 2, base + 96), "3062 BEACH BLVD S", f_addr, CREAM, tracking=6, anchor="mt")

    L["cta"] = shadowed(text_layer(cta), blur=24, opacity=200)

    return L


# ------------------------------------------------------------ shot list ----
# (name, source, t_start, t_end, camera fn)
DUR = 10.0
TOTAL = int(DUR * FPS)

# Landmarks in the top-down source, in normalised window coords.
FEATHER = (0.394, 0.253)   # the chocolate feather latte art
CRUMBLE = (0.488, 0.600)   # the pistachio rubble


def camera(name, t):
    """Returns (source_key, cx, cy, zoom, rot) for a shot-local time."""
    if name == "macro":
        # Open on the feather art - high contrast and graphic, so it reads
        # instantly at thumbnail size - then drift toward the pistachio.
        p = ease_in_out_cubic(t / 1.70)
        return (
            "top",
            lerp(0.425, 0.455, p),
            lerp(0.300, 0.440, p),
            lerp(2.10, 1.90, p),
            lerp(-2.0, 0.6, p),
        )

    if name == "reveal":
        # Three phases so the shot never parks: sit on the foam long enough to
        # register it, decelerate out to the whole glass, then keep drifting.
        if t < 0.28:
            p = t / 0.28
            return ("hero", 0.50, lerp(0.300, 0.311, p), lerp(1.460, 1.432, p), 0.0)
        if t < 1.62:
            p = ease_out_cubic((t - 0.28) / 1.34)
            return ("hero", 0.50, lerp(0.311, 0.478, p), lerp(1.432, 1.020, p), 0.0)
        q = ease_in_out_cubic((t - 1.62) / 0.88)
        return ("hero", 0.50, lerp(0.478, 0.496, q), lerp(1.020, 1.072, q), 0.0)

    if name == "drizzle":
        # hero: slow track down the chocolate running inside the glass
        p = ease_in_out_cubic(t / 2.20)
        return ("hero", 0.512, lerp(0.430, 0.655, p), lerp(1.52, 1.45, p), 0.0)

    if name == "twist":
        # top-down: ease out to the full circle, counter-rotating
        p = ease_out_cubic(t / 1.80)
        return ("top", lerp(0.47, 0.50, p), lerp(0.495, 0.512, p), lerp(1.40, 1.15, p), lerp(2.4, -0.6, p))

    if name == "cta":
        # hero: very slow push in, darkened for type
        p = ease_in_out_cubic(t / 1.80)
        return ("hero", 0.50, lerp(0.487, 0.470, p), lerp(1.05, 1.13, p), 0.0)

    raise ValueError(name)


SHOTS = [
    ("macro", 0.00, 1.70),
    ("reveal", 1.70, 4.20),
    ("drizzle", 4.20, 6.40),
    ("twist", 6.40, 8.20),
    ("cta", 8.20, 10.00),
]

# One text idea on screen at a time: (layer, in, out, fade-in, fade-out)
BEATS = [
    ("hook",    0.22, 1.66, 0.40, 0.16),
    ("sensory", 4.35, 5.45, 0.34, 0.18),
    ("setup",   5.62, 6.38, 0.30, 0.14),   # holds the gap across the hard cut
    ("twist",   6.50, 8.16, 0.24, 0.18),
    ("twist2",  7.15, 8.16, 0.32, 0.18),
    ("cta",     8.52, 10.00, 0.42, 0.01),
]


def shot_at(t):
    for i, (name, s, e) in enumerate(SHOTS):
        if s <= t < e:
            return i, name, s, e
    return len(SHOTS) - 1, SHOTS[-1][0], SHOTS[-1][1], SHOTS[-1][2]


# Hard cuts everywhere except the landing into the end card - dissolving two
# framings of the *same* photograph just reads as a zoom glitch.
DISSOLVE = {3: 0.22}            # twist -> cta
FLASH = {0: 0.10}               # macro -> reveal, a cream frame-flash
DIP = {2: 0.09}                 # drizzle -> twist, a dip to black on the punch


def plate_at(t, src, shot_index=None):
    """The graded photographic plate (no type) at absolute time t."""
    if shot_index is None:
        _, name, s, _ = shot_at(t)
    else:
        name, s, _ = SHOTS[shot_index]
    key, cx, cy, z, rot = camera(name, t - s)
    img = frame_from(src[key], cx, cy, z, rot, handheld(t))
    return grade(img, bloom=0.15 if key == "hero" else 0.10)


def compose(t, src, L):
    """The finished 1080x1920 frame at absolute time t."""
    i, name, s, e = shot_at(t)
    base = plate_at(t, src)

    # cross-dissolve into the next shot
    dd = DISSOLVE.get(i)
    if dd and 0 <= e - t < dd:
        p = ease_in_out_cubic(1 - (e - t) / dd)
        nxt_name, nxt_s, _ = SHOTS[i + 1]
        k2, cx2, cy2, z2, r2 = camera(nxt_name, 0.0)
        nxt = grade(
            frame_from(src[k2], cx2, cy2, z2, r2, handheld(t)),
            bloom=0.15 if k2 == "hero" else 0.10,
        )
        base = Image.blend(base, nxt, p)

    base = apply_vignette(base).convert("RGBA")

    def over(rgba):
        # fade_layer yields None at zero alpha - nothing to composite
        if rgba is None:
            return base
        return Image.alpha_composite(base, rgba)

    # The twist is the emotional turn: knock the plate down hard so the big
    # cream numerals hit, and so the cut itself registers as a beat.
    if name == "twist":
        p = ease_out_cubic((t - s) / 0.28)
        base = over(Image.new("RGBA", (W, H), (6, 5, 4, int(120 * p))))

    # end card gets the same knock-down plus a scrim so the wordmark reads
    if name == "cta":
        p = clamp01((t - s) / 0.5)
        base = over(Image.new("RGBA", (W, H), (6, 5, 4, int(118 * p))))
        base = over(fade_layer(SCRIM_BOTTOM, p * 0.85))

    # the hook sits over the brightest plate in the film - give it a scrim
    hook_beat = next(b for b in BEATS if b[0] == "hook")
    a_hook = band(t, *hook_beat[1:])
    if a_hook > 0.003:
        base = over(fade_layer(SCRIM_TOP, a_hook))

    # ---- type ------------------------------------------------------------
    for key, bs, be, fi, fo in BEATS:
        a = band(t, bs, be, fi, fo)
        if a <= 0.003:
            continue
        _, dy = anim_in(t, bs, fi)
        lay = fade_layer(L[key], a, 0.0 if key == "cta" else dy)
        if lay is not None:
            base = over(lay)

    # ---- cut treatments --------------------------------------------------
    for out_idx, fdur in FLASH.items():
        cut = SHOTS[out_idx][2]
        if 0 <= t - cut < fdur:
            p = 1 - (t - cut) / fdur
            base = over(Image.new("RGBA", (W, H), (*CREAM, int(70 * p * p))))

    for out_idx, fdur in DIP.items():
        cut = SHOTS[out_idx][2]
        if abs(t - cut) < fdur:
            p = 1 - abs(t - cut) / fdur
            base = over(Image.new("RGBA", (W, H), (4, 3, 3, int(215 * p * p))))

    return base.convert("RGB")


def render():
    FRAMES.mkdir(parents=True, exist_ok=True)
    for f in FRAMES.glob("*.png"):
        f.unlink()

    src = load_sources()
    L = build_text_layers()

    for n in range(TOTAL):
        t = n / FPS
        compose(t, src, L).save(FRAMES / f"f{n:05d}.png", compress_level=1)
        if n % 30 == 0:
            print(f"  frame {n}/{TOTAL}  t={t:.2f}  {shot_at(t)[1]}", flush=True)

    print(f"rendered {TOTAL} frames")


if __name__ == "__main__":
    render()
