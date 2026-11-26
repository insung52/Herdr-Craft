# Blocky cats for the mc-* mods (original art: boxes, colours and faces are made up here).
#   python gen_cats.py  ->  cats4/<coat>-{walk,idle,sleep,gift,done}.png (frame strips), <coat>-face(-sm).png, meta.js
#
# Yard cats are drawn with a tiny orthographic box renderer (a little 3D, pixel edges).
#   working  : side view, trots across the yard, stops, turns its body round, trots back
#   idle     : sits facing you; blinks, swishes its tail, tilts its head, flicks an ear
#   off      : a loaf facing you, eyes shut, breathing, z's drifting up
#   blocked  : sits facing you behind a gift, tail going, head tilting up at you
#   done     : sits facing you, happy eyes, an XP orb bobbing beside it
# The list icon (face.png) is a flat, front-on pixel face, drawn by hand below.
import math, os
from PIL import Image, ImageDraw, ImageOps

# Lying cats come in variants so a row of them doesn't look stamped: the body turned a little
# (yaw offsets, degrees) and each of those mirrored. Variant id = 2 * yaw index + mirrored.
LIE_YAWS = [-10, -5, 0, 5, 10]
LIE_VARIANTS = 2 * len(LIE_YAWS)
# Sitting cats (idle, gift, done) get the same yaw offsets, unmirrored: variant id = yaw index.
# The mod gives a cat the same yaw index sitting and lying, and its lie-down starts from that yaw.
SIT_VARIANTS = len(LIE_YAWS)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "cats8")  # bump the folder name when sprites change: the app caches images by path
os.makedirs(OUT, exist_ok=True)
SS = 8

def rgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)

# ── coats ───────────────────────────────────────────────────────────────────────
COATS = {
    "ginger":  dict(B="#eaa04a", M="#c06a22", L="#fbe3bc", E="#58c94a", N="#f08a9c", I="#f4a7b4", pat="tabby"),
    "tuxedo":  dict(B="#33333d", M="#33333d", L="#f1f1f1", E="#f0d64a", N="#f08a9c", I="#e98fa0", pat="tuxedo"),
    "black":   dict(B="#30303b", M="#3d3d4a", L="#30303b", E="#9be05a", N="#6a4a55", I="#5a4a55", pat="plain"),
    "calico":  dict(B="#f4f2ec", M="#e08a32", L="#ffffff", E="#e8c33a", N="#f08a9c", I="#f4a7b4", pat="calico", D="#3a3431"),
    "siamese": dict(B="#efe3cb", M="#55392a", L="#f7eedd", E="#5ec2f5", N="#3a261b", I="#55392a", pat="points"),
    "gray":    dict(B="#9a9ba6", M="#70727e", L="#dcdde2", E="#efc63e", N="#e08ea0", I="#f0a8b6", pat="tabby"),
    "white":   dict(B="#f6f5f0", M="#e2e0d8", L="#ffffff", E="#62bff2", N="#f29aaa", I="#f6b2bf", pat="plain"),
}
PUPIL, GLINT, MOUTH = rgb("#1b1414"), rgb("#ffffff"), rgb("#5a3a34")

# ── flat face icon: the same 5x4-texel face as the yard cats, ears on top ──────
FACE5 = ["I...I", "BBBBB", "EPBPE", "BLNLB", "BLLLB"]

def face_icon(name, S=6):
    c = COATS[name]; pat = c["pat"]
    grid = []
    for y, row in enumerate(FACE5):
        r = []
        for x, ch in enumerate(row):
            if ch == "B" and y >= 1: ch = head_mark(pat, x, y - 1)
            r.append(ch)
        grid.append(r)
    lum = sum(rgb(c["B"])) / 3
    out_c = rgb("#9a9aac") if lum < 90 else shade(rgb(c["B"]), 0.4)
    o = max(1, S // 3)
    w, h = len(grid[0]), len(grid)
    im = Image.new("RGBA", (w * S + 2 * o, h * S + 2 * o), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # outline: the silhouette grown by `o` px
    for y in range(h):
        for x in range(w):
            if grid[y][x] != ".":
                d.rectangle([x * S, y * S, x * S + S - 1 + 2 * o, y * S + S - 1 + 2 * o], fill=out_c + (255,))
    for y in range(h):
        for x in range(w):
            ch = grid[y][x]
            if ch == ".": continue
            col = tex_color(name, ch)
            if ch in "BMD" and y == 1: col = shade(col, 1.08)          # a touch of top light
            d.rectangle([o + x * S, o + y * S, o + x * S + S - 1, o + y * S + S - 1], fill=col + (255,))
    # muzzle reads as a raised block: a thin shadow under it
    d.rectangle([o + 1 * S, o + 5 * S - max(1, S // 6), o + 4 * S - 1, o + 5 * S - 1], fill=shade(tex_color(name, "L"), 0.8) + (255,))
    return im

# ── 3D: textures for the head front (10 x 8 cells) and muzzle front (6 x 4) ─────
# Head front is 5x4 texels and the muzzle 3x2, as on a Minecraft-style cat: few texels, drawn big.
HEAD = {
    "open":   ["BBBBB", "EPBPE", "BBBBB", "BBBBB"],
    "closed": ["BBBBB", "KKBKK", "BBBBB", "BBBBB"],
    "happy":  ["BBBBB", "KKBKK", "BBBBB", "BBBBB"],
}
MUZZLE = ["LNL", "LLL"]

def head_mark(pat, u, v):
    if pat == "tabby" and v == 0 and u in (1, 3): return "M"
    if pat == "calico" and u <= 1 and v <= 2: return "M"
    if pat == "calico" and u >= 4 and v == 0: return "D"
    if pat == "points" and 1 <= u <= 3 and v >= 2: return "M"
    if pat == "tuxedo" and 1 <= u <= 3 and v == 3: return "L"
    return "B"

def tex_color(C, ch):
    c = COATS[C]
    if ch == "B": return rgb(c["B"])
    if ch == "M": return rgb(c["M"])
    if ch == "D": return rgb(c.get("D", c["M"]))
    if ch == "L": return rgb(c["M"]) if c["pat"] == "points" else rgb(c["L"])
    if ch == "E": return rgb(c["E"])
    if ch == "P": return PUPIL
    if ch == "N": return rgb(c["N"])
    if ch == "m": return rgb("#2a1a12") if c["pat"] == "points" else MOUTH
    if ch == "K": return shade(rgb(c["B"]), 0.35) if sum(rgb(c["B"])) > 250 else rgb("#9a9aae")
    if ch == "I": return rgb(c["I"])
    return rgb("#ff00ff")

def cell_color(C, part, face, u, v, nu, nv, eyes, n=None):
    c = COATS[C]; pat = c["pat"]
    base, mark, light = rgb(c["B"]), rgb(c["M"]), rgb(c["L"])
    if part == "gift":
        return rgb("#ffd84a") if (u == nu // 2 or v == nv // 2) else rgb("#d63b3b")
    if part == "head" and face == "front":
        ch = HEAD[eyes][v][u]
        if ch == "B": ch = head_mark(pat, u, v)
        return tex_color(C, ch)
    if part == "muzzle" and face == "front":
        return tex_color(C, MUZZLE[v][u])
    if part == "muzzle":
        return tex_color(C, "L")
    if part == "ear":
        if face == "front": return tex_color(C, "I")
        return mark if pat in ("points", "calico") else base
    if part == "paw":
        return mark if pat == "points" else light if pat != "plain" else shade(base, 1.08)
    col = base
    if pat == "tabby":
        if part == "body" and face in ("side", "back", "top") and u % 3 == 0: col = mark
        if part == "tail" and u % 2 == 0: col = mark
        if part == "head" and face == "top" and u % 2 == 0: col = mark
        if part == "body" and face in ("under", "front"): col = light
    if pat == "tuxedo" and part == "body" and face in ("front", "under"): col = light
    if pat == "calico" and n is not None:
        nx, ny, nz = n                                   # 0..1 across the box (x back->front, y down->up, z near->far)
        if part == "body":
            if face in ("under", "front") or ny < 0.35: col = base
            elif nx < 0.45: col = mark                    # orange saddle over the hips
            elif nx < 0.62 and nz > 0.25: col = rgb(c["D"])   # black patch mid-back
            elif nx > 0.8 and ny > 0.6: col = mark        # orange at the shoulders
        elif part == "tail":
            col = mark if nx < 0.6 else rgb(c["D"])
        elif part == "head" and face != "front":
            col = mark if nz < 0.5 else rgb(c["D"])
        elif part == "leg" and face == "top":
            col = mark
    if pat == "points" and part == "tail": col = mark
    if pat == "points" and part == "leg" and v >= nv - 2: col = mark
    return col

LIGHT = {"top": 1.15, "side": 1.0, "front": 0.95, "rear": 0.8, "back": 0.75, "under": 0.6}

class Box:
    """An axis box with rotations [(axis, degrees, pivot)] applied in order; `cell` is the texture cell size."""
    def __init__(self, part, x0, x1, y0, y1, z0, z1, rots=(), cell=1.0):
        self.part, self.b, self.rots, self.cell = part, (x0, x1, y0, y1, z0, z1), list(rots), cell

    def xf(self, x, y, z):
        for ax, deg, (px, py, pz) in self.rots:
            a = math.radians(deg); ca, sa = math.cos(a), math.sin(a)
            x, y, z = x - px, y - py, z - pz
            if ax == "z": x, y = x * ca - y * sa, x * sa + y * ca
            elif ax == "x": y, z = y * ca - z * sa, y * sa + z * ca
            else: x, z = x * ca + z * sa, -x * sa + z * ca
            x, y, z = x + px, y + py, z + pz
        return x, y, z

    def faces(self):
        x0, x1, y0, y1, z0, z1 = self.b
        return [
            ("side",  (x0, y1, z0), (x1 - x0, 0, 0), (0, y0 - y1, 0), (0, 0, -1)),
            ("back",  (x1, y1, z1), (x0 - x1, 0, 0), (0, y0 - y1, 0), (0, 0, 1)),
            ("top",   (x0, y1, z1), (x1 - x0, 0, 0), (0, 0, z0 - z1), (0, 1, 0)),
            ("under", (x0, y0, z0), (x1 - x0, 0, 0), (0, 0, z1 - z0), (0, -1, 0)),
            ("front", (x1, y1, z0), (0, 0, z1 - z0), (0, y0 - y1, 0), (1, 0, 0)),
            ("rear",  (x0, y1, z1), (0, 0, z0 - z1), (0, y0 - y1, 0), (-1, 0, 0)),
        ]

class Cam:
    def __init__(self, yaw=36, pitch=20, unit=2):
        self.t, self.p, self.unit = math.radians(yaw), math.radians(pitch), unit

    def rot(self, x, y, z):
        t, p = self.t, self.p
        sx = x * math.cos(t) + z * math.sin(t)
        d = -x * math.sin(t) + z * math.cos(t)
        return sx, y * math.cos(p) + d * math.sin(p), d * math.cos(p) - y * math.sin(p)

def render(boxes, C, cam, eyes="open", w=170, h=110, ox=85, oy=96):
    S = SS * cam.unit
    im = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    polys = []
    for b in boxes:
        for name, o, U, V, n in b.faces():
            p0 = b.xf(*o); p1 = b.xf(*[o[i] + n[i] for i in range(3)])
            if cam.rot(*[p1[i] - p0[i] for i in range(3)])[2] >= -1e-6:
                continue
            nu = max(1, round(math.hypot(*U) / b.cell)); nv = max(1, round(math.hypot(*V) / b.cell))
            for i in range(nu):
                for j in range(nv):
                    pts = [cam.rot(*b.xf(*[o[k] + U[k] * a / nu + V[k] * c / nv for k in range(3)]))
                           for a, c in ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))]
                    depth = sum(q[2] for q in pts) / 4
                    cp = [o[k] + U[k] * (i + 0.5) / nu + V[k] * (j + 0.5) / nv for k in range(3)]
                    x0, x1, y0, y1, z0, z1 = b.b
                    nrm = ((cp[0] - x0) / max(1e-6, x1 - x0), (cp[1] - y0) / max(1e-6, y1 - y0), (cp[2] - z0) / max(1e-6, z1 - z0))
                    col = shade(cell_color(C, b.part, name, i, j, nu, nv, eyes, nrm), LIGHT[name])
                    polys.append((depth, [((ox / cam.unit + q[0]) * S, (oy / cam.unit - q[1]) * S) for q in pts], col))
    polys.sort(key=lambda q: -q[0])
    for _, pts, col in polys:
        dr.polygon(pts, fill=col + (255,))
    return im.resize((w, h), Image.NEAREST)

# ── body parts ──────────────────────────────────────────────────────────────────
def head(hx, hy, tilt=0.0, nod=0.0, ear=0.0, big=1.0, turn=0.0):
    """Head 5 deep; front 5x4 texels, muzzle 3x2, ears 1x1 (x2 deep). `big` scales the texel."""
    c = big; W, H = 5 * c, 4 * c
    piv = (hx + 2.5, hy, 0)
    R = [("x", tilt, piv), ("z", nod, piv), ("y", turn, (hx + 2.5, hy, 0))]
    return [
        Box("head", hx, hx + 5, hy, hy + H, -W / 2, W / 2, R, cell=c),
        Box("muzzle", hx + 5, hx + 5 + c * 0.8, hy, hy + 2 * c, -1.5 * c, 1.5 * c, R, cell=c),
        Box("ear", hx + 1.5, hx + 3.5, hy + H, hy + H + c, -W / 2, -W / 2 + c, [("x", -ear, (hx + 2.5, hy + H, -W / 2 + 0.5 * c))] + R, cell=c),
        Box("ear", hx + 1.5, hx + 3.5, hy + H, hy + H + c, W / 2 - c, W / 2, R, cell=c),
    ]

def leg(x, z, ang, top=6.0, length=6.0, part="leg"):
    return Box(part, x, x + 2, top - length, top, z, z + 2, [("z", ang, (x + 1, top, z + 1))])

def paw_tip(x, z, ang, top, length):
    return Box("paw", x - 0.01, x + 2.01, top - length - 0.01, top - length + 1, z - 0.01, z + 2.01, [("z", ang, (x + 1, top, z + 1))])

def tail_chain(x, y, z, angles, seg=3.0, plane="z"):
    """Tail as a chain of thin segments; each angle is relative to the previous (degrees, up = positive)."""
    out, a = [], 180.0
    for k, da in enumerate(angles):
        a += -da
        rad = math.radians(a)
        if plane == "z":
            ex, ey, ez = x + seg * math.cos(rad), y + seg * math.sin(rad), z
        else:  # lies on the ground, curling in the x-z plane
            ex, ey, ez = x + seg * math.cos(rad), y, z + seg * math.sin(rad)
        cx, cy, cz = (x + ex) / 2, (y + ey) / 2, (z + ez) / 2
        b = Box("tail", cx - seg / 2 - 0.15, cx + seg / 2 + 0.15, cy - 0.5, cy + 0.5, cz - 0.5, cz + 0.5,
                [("z" if plane == "z" else "y", (a - 180) if plane == "z" else -(a - 180), (cx, cy, cz))])
        out.append(b); x, y, z = ex, ey, ez
    return out

# ── poses ───────────────────────────────────────────────────────────────────────
def pose_run(ph, stand=0.0):
    """ph: gait phase (radians). stand=1 blends to a standing stop (for the turn)."""
    k = 1.0 - stand
    s = math.sin(ph)
    by = 6 + 0.5 * k * max(0.0, math.sin(2 * ph))
    pitch = 3 * k * math.sin(ph + 0.8)
    A = 34 * k
    body = Box("body", -8, 7, by, by + 4, -2, 2, [("z", pitch, (0, by + 2, 0))])
    legs = []
    for (x, z, off, sign) in ((4, -2, 0.0, 1), (4, 0, 0.9, 1), (-7, -2, math.pi, 1), (-7, 0, math.pi + 0.9, 1)):
        ang = A * math.sin(ph + off)
        legs += [leg(x, z, ang, top=by + 0.5), paw_tip(x, z, ang, by + 0.5, 6)]
    hd = head(6, by + 2.6 + 0.4 * k * math.sin(ph * 2 + 1.2), nod=-2 * k * math.sin(ph + 1.5))
    tl = tail_chain(-8, by + 3.5, 0, [40 + 6 * k * math.sin(ph), 16 + 10 * k * math.sin(ph + 1.3), 12], seg=3.0)
    return [body] + legs + hd + tl

def pose_sit(tilt=0.0, ear=0.0, tail_sw=0.0, head_dy=0.0):
    # a chubby sitting cat seen from the front: upright chest, haunches behind, short front legs, big head
    boxes = [Box("body", -1.5, 2.5, 0, 6.2, -2.3, 2.3)]                        # chest (its front is the belly colour)
    boxes += [Box("leg", -5, -0.5, 0, 3.4, -2.8, 2.8)]                         # haunches
    boxes += [Box("paw", -1.5, 1.0, 0, 1, -3.0, -1.6), Box("paw", -1.5, 1.0, 0, 1, 1.6, 3.0)]
    boxes += [leg(2.3, -2.0, 0, top=5.0, length=5.0), paw_tip(2.3, -2.0, 0, 5.0, 5.0),
              leg(2.3, 0.0, 0, top=5.0, length=5.0), paw_tip(2.3, 0.0, 0, 5.0, 5.0)]
    boxes += head(-2.0, 6.0 + head_dy, tilt=tilt, ear=ear, big=4 / 3)
    boxes += tail_chain(-4.5, 0.5, -2.4, [-90, -30 - tail_sw * 0.4, -45 - tail_sw, -35 - tail_sw], seg=2.2, plane="y")
    return boxes

def pose_lie(t=1.0, tilt=0.0, ear=0.0, tail_sw=0.0, breath=0.0, nod=0.0, drop=0.0, turn=0.0):
    """t=0 sits like pose_sit, t=1 lies down facing you (front paws out, head up)."""
    top = 6.2 - 2.9 * t + breath
    boxes = [Box("body", -1.5 - 4.5 * t, 2.5, 0, top, -2.3, 2.3)]
    boxes += [Box("leg", -5, -0.5, 0, 3.4 - 0.6 * t, -2.8, 2.8)]
    L = 5.0 * (1 - t)
    if L > 1.2:
        boxes += [leg(2.3, -2.0, 0, top=L, length=L), paw_tip(2.3, -2.0, 0, L, L),
                  leg(2.3, 0.0, 0, top=L, length=L), paw_tip(2.3, 0.0, 0, L, L)]
    else:
        boxes += [Box("paw", 2.3, 2.3 + 3.2 * t, 0, 1.2, -2.0, -0.2), Box("paw", 2.3, 2.3 + 3.2 * t, 0, 1.2, 0.2, 2.0)]
    boxes += head(-2.0 + 1.6 * t + drop * 0.6, 6.0 - 3.3 * t + breath * 0.6 - drop, tilt=tilt, ear=ear, nod=nod, big=4 / 3, turn=turn)
    boxes += tail_chain(-4.5 - 1.0 * t, 0.5, -2.4, [-90, -30 - tail_sw * 0.4, -45 - tail_sw, -35 - tail_sw], seg=2.2, plane="y")
    return boxes

def gift(dy=0.0):
    return [Box("gift", 4.6, 8.0, dy, 3.4 + dy, -1.7, 1.7)]

# ── output ──────────────────────────────────────────────────────────────────────
def save_gif(path, frames, ms):
    """One shared palette for every frame, index 255 = transparent in every frame."""
    w, h = frames[0].size
    strip = Image.new("RGB", (w, h * len(frames)), (0, 0, 0))
    for i, f in enumerate(frames):
        strip.paste(f.convert("RGB"), (0, i * h), f)
    pal_img = strip.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    palette = pal_img.getpalette()[:255 * 3] + [0, 0, 0]
    ref = Image.new("P", (1, 1)); ref.putpalette(palette)
    out = []
    for f in frames:
        p = f.convert("RGB").quantize(palette=ref, dither=Image.Dither.NONE)
        p.paste(255, mask=f.getchannel("A").point(lambda a: 255 if a < 128 else 0))
        p.info["transparency"] = 255
        out.append(p)
    durs = ms if isinstance(ms, list) else [ms] * len(frames)
    out[0].save(path, save_all=True, append_images=out[1:], duration=durs, loop=0, disposal=2,
                transparency=255, optimize=False)

def crop_all(frames, pad=1, ground=None):
    box = None
    for f in frames:
        b = f.getchannel("A").point(lambda a: 255 if a >= 128 else 0).getbbox()
        if b: box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
    l, t, r, btm = box
    global LAST_BTM; LAST_BTM = btm
    # the bottom is the lowest drawn pixel (paws), so the mod can stand the cat right on the grass
    return [f.crop((max(0, l - pad), max(0, t - pad), r + pad, btm)) for f in frames]

LAST_BTM = 0
def body_bottom(boxes, C, cam):
    """Lowest drawn row of everything but the tail (uncropped canvas rows): where a lying cat rests."""
    b = render([q for q in boxes if q.part != "tail"], C, cam).getchannel("A").point(lambda a: 255 if a >= 128 else 0).getbbox()
    return b[3] if b else 0

def px(im, pts, color):
    d = ImageDraw.Draw(im)
    for x, y in pts:
        if 0 <= x < im.width and 0 <= y < im.height:
            d.point((x, y), fill=rgb(color) + (255,))

Z_GLYPH = [(0, 0), (1, 0), (2, 0), (2, 1), (1, 2), (0, 3), (1, 3), (2, 3)]
# Experience orb: round, dark-green rim, lime-to-yellow body that shimmers, a bright glint.
# Experience orb: octagonal blob, dark rim, rings getting lighter inward, a darker core;
# its colour drifts between green and yellow-green like the game's.
ORB = ["...oooo...", ".ooggggoo.", ".ogGGGGgo.", "ogGGllGGgo", "ogGlcclGgo", "ogGlcclGgo", "ogGGllGGgo", ".ogGGGGgo.", ".ooggggoo.", "...oooo..."]
ORB_PH = [{"o": "#1b6b14", "g": "#2a9a1e", "G": "#3cc42c", "l": "#7ef05a", "c": "#2e8a22"},
          {"o": "#3f7410", "g": "#6aae1c", "G": "#9ad42a", "l": "#d6f75c", "c": "#5f9a1a"}]

def orb(im, x, y, i, S=2):
    d = ImageDraw.Draw(im); ph = ORB_PH[(i // 2) % 2]
    for j, row in enumerate(ORB):
        for k, ch in enumerate(row):
            if ch in ph:
                d.rectangle([x + k * S, y + j * S, x + k * S + S - 1, y + j * S + S - 1], fill=rgb(ph[ch]) + (255,))

SIDE = lambda yaw=36: Cam(yaw, 20, 3)
FRONT = Cam(84, 12, 3)
GROUND = 96  # oy: world y=0 lands on this canvas row

def save_strip(path, frames):
    """Frames side by side in one PNG; the mod shows one at a time (this app shows only a GIF's first frame)."""
    w, h = frames[0].size
    strip = Image.new("RGBA", (w * len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        strip.paste(f, (i * w, 0), f)
    strip.save(path)

META = {}

def build(C):
    stride = 12          # gait frames per stride (shown 100 ms each)
    # ── working: unique frames = run right (8), turn (9), run left (8), turn back (9)
    runR = [(36, 2 * math.pi * i / stride, 0.0, "open") for i in range(stride)]
    turnA = [(36, 0, k / 2, "open") for k in (1, 2)] + [(36 + 108 * k / 5, 0, 1.0, "closed" if k in (2, 3) else "open") for k in range(1, 6)] + [(144, 0, 1 - k / 2, "open") for k in (1, 2)]
    runL = [(144, 2 * math.pi * i / stride, 0.0, "open") for i in range(stride)]
    turnB = [(144, 0, k / 2, "open") for k in (1, 2)] + [(144 - 108 * k / 5, 0, 1.0, "closed" if k in (2, 3) else "open") for k in range(1, 6)] + [(36, 0, 1 - k / 2, "open") for k in (1, 2)]
    spec = runR + turnA + runL + turnB
    walk = crop_all([render(pose_run(ph, st), C, SIDE(yaw), eyes) for (yaw, ph, st, eyes) in spec], ground=GROUND)
    save_strip(os.path.join(OUT, f"{C}-walk.png"), walk)
    W, step = 240, 3
    fw = walk[0].width
    xs = list(range(0, W - fw + 1, step))
    A0, L0, B0 = stride, stride + 9, 2 * stride + 9      # where turnA, runL and turnB start in the strip
    seq = [[x, k % stride] for k, x in enumerate(xs)]
    seq += [[xs[-1], A0 + k // 2] for k in range(18)]          # each turn frame shown twice
    seq += [[x, L0 + k % stride] for k, x in enumerate(reversed(xs))]
    seq += [[0, B0 + k // 2] for k in range(18)]
    META["walk"] = {"w": fw, "h": walk[0].height, "n": len(walk), "span": W, "seq": seq}

    # ── idle: sits facing you; tail swish, slow head tilt, one blink, one ear flick (24 frames)
    n = 48
    idle_all = crop_all([render(pose_sit(tilt=5 * math.sin(2 * math.pi * i / n), ear=25 if i in (12, 13, 14) else 0,
                                         tail_sw=22 * math.sin(4 * math.pi * i / n)), C, Cam(84 + d, 12, 3), "closed" if i in (30, 31, 32) else "open")
                         for d in LIE_YAWS for i in range(n)], ground=GROUND)
    for v in range(SIT_VARIANTS):
        save_strip(os.path.join(OUT, f"{C}-idle-{v}.png"), idle_all[v * n:(v + 1) * n])
    idle = idle_all[2 * n:3 * n]
    META["idle"] = {"w": idle[0].width, "h": idle[0].height, "n": n, "variants": SIT_VARIANTS}

    # ── off: sleeping loaf, breathing, z's rising (24 frames), in every lying variant
    NS = 24
    sl_specs = [(pose_lie(1.0, breath=0.3 * (0.5 - 0.5 * math.cos(2 * math.pi * i / NS)), drop=1.2, turn=52, tilt=-10, tail_sw=-25), Cam(32 + d, 18, 3))
                for d in LIE_YAWS for i in range(NS)]
    sl_all = crop_all([render(bx, C, cam, "closed") for bx, cam in sl_specs], ground=GROUND)
    # how many rows the strip hangs below the body (the tail): the mod sinks it that far into the grass
    sl_bot = [body_bottom(bx, C, cam) for bx, cam in sl_specs]
    sl_sink = [LAST_BTM - min(sl_bot[k * NS:(k + 1) * NS], key=lambda v: -v) for k in range(len(LIE_YAWS))]
    for v in range(LIE_VARIANTS):
        sl, mir = sl_all[(v // 2) * NS:(v // 2 + 1) * NS], v % 2 == 1
        out = []
        for i, f in enumerate(sl):
            c = Image.new("RGBA", (f.width + 12, f.height + 18), (0, 0, 0, 0))
            c.paste(ImageOps.mirror(f) if mir else f, (12 if mir else 0, 18), ImageOps.mirror(f) if mir else f)
            for k in range(3):
                tt = ((i / NS) + k / 3) % 1.0
                if tt < 0.85:
                    big = 2 if tt > 0.35 else 1
                    zx, zy = f.width - 6 + int(8 * tt), 16 - int(16 * tt)
                    if mir: zx = c.width - zx - 3 * big      # the z's rise from the head, which is now on the left
                    px(c, [(zx + a * big + da, zy + b * big + db) for a, b in Z_GLYPH for da in range(big) for db in range(big)],
                       "#ffffff" if tt < 0.6 else "#b8c6ea")
            out.append(c)
        save_strip(os.path.join(OUT, f"{C}-sleep-{v}.png"), out)
    META["sleep"] = {"w": out[0].width, "h": out[0].height, "n": NS, "variants": LIE_VARIANTS,
                     "sink": [sl_sink[v // 2] for v in range(LIE_VARIANTS)]}

    # ── checked (idle a while): lies down once, then rests awake — blinks, tail flicks
    ld = crop_all([render(pose_lie(t), C, FRONT, "open") for t in (0.15, 0.35, 0.55, 0.75, 0.9, 1.0)]
                  + [render(pose_lie(1.0), C, FRONT, "open")], ground=GROUND)
    rest = ld[-1:]
    frames, bots = [], []
    for d in LIE_YAWS:
        bots += [body_bottom(pose_lie(t, turn=50 * t), C, Cam(84 + d - 50 * t, 12 + 6 * t, 3)) for t in (0.15, 0.35, 0.55, 0.75, 0.9, 1.0)]
        bots += [body_bottom(pose_lie(1.0, turn=50, tilt=3 * math.sin(2 * math.pi * i / 48)), C, Cam(34 + d, 18, 3)) for i in range(48)]      # per yaw: 6 lie-down frames (turning from facing you to the final yaw), then 48 resting
        frames += [render(pose_lie(t, turn=50 * t), C, Cam(84 + d - 50 * t, 12 + 6 * t, 3), "open") for t in (0.15, 0.35, 0.55, 0.75, 0.9, 1.0)]
        frames += [render(pose_lie(1.0, turn=50, tilt=3 * math.sin(2 * math.pi * i / 48), ear=25 if i in (34, 35) else 0,
                                   tail_sw=16 * math.sin(2 * math.pi * i / 24)), C, Cam(34 + d, 18, 3), "closed" if i in (16, 17, 18) else "open")
                   for i in range(48)]
    allf = crop_all(frames, ground=GROUND)
    ld_sink = [[LAST_BTM - b for b in bots[k * 54:k * 54 + 6]] for k in range(len(LIE_YAWS))]      # per lie-down frame
    rs_sink = [LAST_BTM - max(bots[k * 54 + 6:(k + 1) * 54]) for k in range(len(LIE_YAWS))]
    for v in range(LIE_VARIANTS):
        both = allf[(v // 2) * 54:(v // 2 + 1) * 54]
        if v % 2: both = [ImageOps.mirror(f) for f in both]
        save_strip(os.path.join(OUT, f"{C}-liedown-{v}.png"), both[:6])
        save_strip(os.path.join(OUT, f"{C}-rest-{v}.png"), both[6:])
    META["liedown"] = {"w": both[0].width, "h": both[0].height, "n": 6, "variants": LIE_VARIANTS,
                       "sinkF": [ld_sink[v // 2] for v in range(LIE_VARIANTS)]}
    META["rest"] = {"w": both[0].width, "h": both[0].height, "n": 48, "variants": LIE_VARIANTS,
                    "sink": [rs_sink[v // 2] for v in range(LIE_VARIANTS)]}

    # ── blocked: behind a gift, looking up at you (16 frames)
    gf_all = crop_all([render(pose_sit(tilt=-7 * math.sin(2 * math.pi * i / 32), tail_sw=30 * math.sin(4 * math.pi * i / 32), head_dy=0.3)
                              + gift(0.4 if i in (8, 9, 24, 25) else 0.0), C, Cam(84 + d, 12, 3), "open") for d in LIE_YAWS for i in range(32)], ground=GROUND)
    for v in range(SIT_VARIANTS):
        save_strip(os.path.join(OUT, f"{C}-gift-{v}.png"), gf_all[v * 32:(v + 1) * 32])
    gf = gf_all[64:96]
    META["gift"] = {"w": gf[0].width, "h": gf[0].height, "n": 32, "variants": SIT_VARIANTS}

    # ── done: happy eyes, an XP orb bobbing right above the head (16 frames)
    full, heads = [], []
    for d in LIE_YAWS:
        for i in range(32):
            bx = pose_sit(tilt=4 * math.sin(2 * math.pi * i / 32), tail_sw=14 * math.sin(2 * math.pi * i / 32))
            full.append(render(bx, C, Cam(84 + d, 12, 3), "happy" if (i // 8) % 2 == 0 else "open"))
            heads.append(render([q for q in bx if q.part in ("head", "muzzle", "ear")], C, Cam(84 + d, 12, 3)))
    box = None
    for f in full:
        bb = f.getchannel("A").point(lambda a: 255 if a >= 128 else 0).getbbox()
        box = bb if box is None else (min(box[0], bb[0]), min(box[1], bb[1]), max(box[2], bb[2]), max(box[3], bb[3]))
    l, t, r, btm = box[0] - 1, box[1], box[2] + 1, box[3]
    TOP = 26
    out2 = []
    for i, (f, hd) in enumerate(zip(full, heads)):
        hb = hd.getchannel("A").point(lambda a: 255 if a >= 128 else 0).getbbox()
        c = Image.new("RGBA", (r - l, btm - t + TOP), (0, 0, 0, 0))
        c.paste(f.crop((l, t, r, btm)), (0, TOP))
        cxh = (hb[0] + hb[2]) // 2 - l
        y = (hb[1] - t + TOP) - 22 + round(2 * math.sin(2 * math.pi * (i % 32) / 32))
        orb(c, cxh - 10, y, i % 32)
        out2.append(c)
    for v in range(SIT_VARIANTS):
        save_strip(os.path.join(OUT, f"{C}-done-{v}.png"), out2[v * 32:(v + 1) * 32])
    out2 = out2[64:96]
    META["done"] = {"w": out2[0].width, "h": out2[0].height, "n": 32, "variants": SIT_VARIANTS}

    face = face_icon(C)
    face.save(os.path.join(OUT, f"{C}-face.png"))
    face_icon(C, 3).save(os.path.join(OUT, f"{C}-face-sm.png"))
    return [walk[0], walk[12], idle[0], gf[0], out2[0], out[0], face]

if __name__ == "__main__":
    for f in os.listdir(OUT):
        os.remove(os.path.join(OUT, f))
    rows = []
    for C in COATS:
        rows.append(build(C))
    W = max(sum(i.width + 8 for i in r) for r in rows) + 8
    H = sum(max(i.height for i in r) + 8 for r in rows) + 8
    sheet = Image.new("RGBA", (W, H), (18, 24, 49, 255)); y = 8
    for r in rows:
        x = 8; mh = max(i.height for i in r)
        for im in r:
            sheet.paste(im, (x, y + mh - im.height), im); x += im.width + 8
        y += mh + 8
    sheet.resize((W * 3, H * 3), Image.NEAREST).save(os.path.join(HERE, "_cats_preview.png"))
    import json
    with open(os.path.join(OUT, "meta.js"), "w", encoding="utf-8") as f:
        f.write("// generated by gen_cats.py: frame size, count (and the walk's path) of each sprite strip\n")
        f.write("export const META = " + json.dumps(META) + ";\n")
    print("ok", {k: (v["w"], v["h"], v["n"]) for k, v in META.items()})
