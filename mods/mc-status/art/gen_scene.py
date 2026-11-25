# Sky backgrounds and yard scenery for the minecraft layout (original pixel art).
#   python gen_scene.py -> scene/sky-day.png, scene/sky-night.png, scene/<prop>.png
import os, random, math
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "scene")
os.makedirs(OUT, exist_ok=True)

def rgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

# ── skies: 1920x1080, 8 px blocks, flat colour bands like the game's sky ────────
def sky(name, bands, clouds, cloud_c, under_c, body, ridges=None):
    W, H, B = 1920, 1080, 8
    im = Image.new("RGB", (W, H), rgb(bands[0]))
    d = ImageDraw.Draw(im)
    n = len(bands)
    for i, c in enumerate(bands):
        d.rectangle([0, i * H // n, W, (i + 1) * H // n], fill=rgb(c))
    rnd = random.Random(7 if name == "day" else 11)
    if name == "night":
        for _ in range(170):
            x, y = rnd.randrange(0, W // B) * B, rnd.randrange(0, int(H * 0.7) // B) * B
            s = B if rnd.random() < 0.25 else B // 2
            d.rectangle([x, y, x + s - 1, y + s - 1], fill=rgb(rnd.choice(["#ffffff", "#e8ecff", "#fff5c8"])))
    body(d, W, H, B)
    for _ in range(clouds):
        cw = rnd.randrange(10, 26) * B * 2; ch = rnd.randrange(3, 5) * B
        x, y = rnd.randrange(-200, W), rnd.randrange(40, int(H * 0.45))
        d.rectangle([x, y, x + cw, y + ch], fill=rgb(cloud_c))
        d.rectangle([x + B * 3, y - B * 2, x + cw - B * 6, y], fill=rgb(cloud_c))
        d.rectangle([x, y + ch - B, x + cw, y + ch], fill=rgb(under_c))
    if ridges:
        for seed, amp, base_h, col, top, snow in ridges:
            for x in range(0, W, B):
                t = x / W * 2 * math.pi
                h = base_h + amp * (0.6 * (1 - abs(math.sin(t * 2.2 + seed))) + 0.3 * (1 - abs(math.sin(t * 5 + seed * 2))) + 0.1 * math.sin(t * 17 + seed * 3)) - amp * 0.45
                h = max(B, int(h // B) * B)
                d.rectangle([x, H - h, x + B - 1, H - 1], fill=rgb(col))
                if top: d.rectangle([x, H - h, x + B - 1, H - h + B - 1], fill=rgb(top))
                if snow and h > base_h + amp * 0.25: d.rectangle([x, H - h, x + B - 1, H - h + 3 * B - 1], fill=rgb(snow))
    im.save(os.path.join(OUT, f"sky2-{name}.png"), optimize=True)

def sun(d, W, H, B):
    x, y = W - 360, 90
    d.rectangle([x - B * 3, y - B * 3, x + B * 15, y + B * 15], fill=rgb("#fff1a8"))
    d.rectangle([x, y, x + B * 12, y + B * 12], fill=rgb("#fffbe0"))

def moon(d, W, H, B):
    # a square, blocky crescent like the game's moon phases: lit band on the right, craters
    x, y = W - 360, 90
    inner = [11, 9, 8, 8, 7, 7, 7, 7, 8, 8, 9, 11]
    for r, i0 in enumerate(inner):
        d.rectangle([x + i0 * B, y + r * B, x + 12 * B - 1, y + (r + 1) * B - 1], fill=rgb("#eef0dc"))
    for cx, cy in ((9, 2), (8, 5), (10, 7), (9, 9)):
        d.rectangle([x + cx * B, y + cy * B, x + (cx + 1) * B - 1, y + (cy + 1) * B - 1], fill=rgb("#c9cbb2"))

sky("day", ["#5f9ff2", "#6ba9f5", "#78b3f7", "#86bdf8", "#94c6f9", "#a3cffa"], 14, "#ffffff", "#dfe8f3", sun,
    [(1.3, 330, 230, "#9db4d6", None, "#f2f6fb"), (4.1, 150, 110, "#6d9a5a", "#86b86a", None)])
sky("night", ["#070b1c", "#0a1024", "#0d152d", "#111b38", "#152143", "#1a284f"], 7, "#2a3558", "#222b48", moon,
    [(1.3, 330, 230, "#27315a", None, "#59648a"), (4.1, 150, 110, "#1a2a2a", "#22382f", None)])

# ── props, drawn at 1 px per texel then scaled x3 ───────────────────────────────
PAL = {
    "t": "#6b4a2b", "T": "#4f361f", "b": "#e8e4d8", "B": "#3a3a3a",          # oak trunk, birch bark
    "l": "#3f8f2f", "L": "#2f6f22", "m": "#57a83f", "n": "#6fbf4a", "o": "#8bc25a", "O": "#6aa543",  # leaves
    "r": "#d6262b", "R": "#9e1a1e", "y": "#f6d531", "Y": "#d9a50e", "c": "#4a7bf2", "C": "#2c55c8",
    "p": "#b35ad8", "P": "#7e35a8", "w": "#f4f4f4", "g": "#3a8a2a", "G": "#5cae3c",
    "s": "#9bd35a", "S": "#6ca83c", "k": "#3a2a18", "x": "#dfe8f3",
}
PROPS = {
    "oak": [
        "...LllLLllL...", "..LlmmlLmmlL..", ".LlmnmmlmnmlL.", "LlmmmLmmmmLmlL", "LmnmlmmnmlmmnL",
        "LlmmmlmLmmmllL", ".LlmLmmmmlmL..", "..LlllmLllL...", "......tT......", "......tT......",
        "......tT......", "......tT......", "......tT......", ".....ttTT.....",
    ],
    "birch": [
        "...OooOO...", "..OoooOoO..", ".OoOooooOO.", "OooooOooooO", "OoOoooOoOoO", ".OooOooooO.",
        "..OOooOOO..", ".....b.....", ".....B.....", ".....b.....", ".....b.....", ".....B.....",
        ".....b.....", ".....b.....", "....bBb....",
    ],
    "poppy": [".r.", "rRr", ".r.", ".g.", "gg.", ".g."],
    "dandelion": ["yYy", "YyY", ".g.", ".gg", ".g."],
    "cornflower": [".c.", "cCc", ".c.", "gg.", ".g."],
    "allium": [".pP.", "pPpP", ".Pp.", "..g.", ".gg.", "..g."],
    "tuft": ["G...G", "Gg.gG", ".gGg.", ".ggg."],
    "cane": [".s.", ".S.", ".s.", "ss.", ".S.", ".s.", ".sS", ".S.", ".s.", ".s."],
    "lily": [".GGG.", "GgGgG", ".GGG."],
    "tulip": ["r.r", "rRr", "rRr", ".g.", "gg.", ".g."],
    "oxeye": [".w.", "wyw", ".w.", ".g.", ".gg", ".g."],
    "cloud": ["....wwwwwww.......", "..wwwwwwwwwwwww...", "wwwwwwwwwwwwwwwwww", "wwwwwwwwwwwwwwwwww", "xxxxxxxxxxxxxxxxxx"],
}

def prop(name, rows, S=4):
    w, h = len(rows[0]), len(rows)
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for y, r in enumerate(rows):
        assert len(r) == w, (name, r)
        for x, ch in enumerate(r):
            if ch != ".":
                d.rectangle([x * S, y * S, x * S + S - 1, y * S + S - 1], fill=rgb(PAL[ch]) + (255,))
    im.save(os.path.join(OUT, f"{name}.png"))
    return im.size

# ── mountains behind the yard: two blocky ridges, 4 px steps ────────────────────
import math
def mountains(name, far, far_snow, near, near_top):
    W, H, B = 3200, 72, 4
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    def ridge(seed, amp, base, col, top=None, snow=None):
        for x in range(0, W, B):
            t = x / W * 2 * math.pi
            h = base + amp * (0.6 * (1 - abs(math.sin(t * 6 + seed))) + 0.3 * (1 - abs(math.sin(t * 13 + seed * 2))) + 0.1 * math.sin(t * 41 + seed * 3)) - amp * 0.5
            h = max(4, int(h // B) * B)
            d.rectangle([x, H - h, x + B - 1, H - 1], fill=rgb(col) + (255,))
            if top: d.rectangle([x, H - h, x + B - 1, H - h + B - 1], fill=rgb(top) + (255,))
            if snow and h > base + amp * 0.2: d.rectangle([x, H - h, x + B - 1, H - h + 2 * B - 1], fill=rgb(snow) + (255,))
    ridge(1.3, 50, 40, far, snow=far_snow)
    ridge(4.1, 26, 20, near, top=near_top)
    im.save(os.path.join(OUT, f"mountains-{name}.png"))

if __name__ == "__main__":
    mountains("day", "#9db4d6", "#f2f6fb", "#5f8f4a", "#78b05a")
    mountains("night", "#26304f", "#56607e", "#1b2a26", "#24382f")
    sizes = {k: prop(k, v, 4 if k in ("oak", "birch", "cane") else 3) for k, v in PROPS.items()}
    print("ok", sizes)

# ── the yard's ground baked into one picture (grass, dirt, specks, flowers, pond, lily) ──
# The mod draws this one image instead of ~80 small pieces on every redraw.
POND_X, POND_W = 1180, 84

def yard_ground():
    W, H, G = 3200, 40, 16                   # G = ground height at the bottom
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    top = H - G
    d.rectangle([0, top, W - 1, H - 1], fill=rgb("#7a4e2b"))
    d.rectangle([0, top, W - 1, top + 3], fill=rgb("#5aa83a"))
    d.rectangle([0, top, W - 1, top], fill=rgb("#7ccd4c"))
    d.rectangle([0, top + 4, W - 1, top + 4], fill=rgb("#3e7f27"))
    for i in range(W // 37 + 1):
        x = i * 37 + (i * 17) % 13
        y = top + 7 + (i % 3) * 3
        d.rectangle([x, y, x + 2, y + 2], fill=rgb("#5e3b1f" if i % 3 else "#9a6a3f"))
    d.rectangle([POND_X, top, POND_X + POND_W - 1, H - 4], fill=rgb("#3f76e4"))
    d.rectangle([POND_X, top, POND_X + POND_W - 1, top + 1], fill=rgb("#6f9cf2"))
    rnd = random.Random(3)
    names = ["poppy", "dandelion", "cornflower", "tulip", "oxeye", "allium", "tuft", "tuft"]
    x = 150
    while x < W - 20:
        if not (POND_X - 30 < x < POND_X + POND_W + 30):
            n = names[rnd.randrange(len(names))]
            p = Image.open(os.path.join(OUT, f"{n}.png"))
            im.paste(p, (x, top - p.height), p)
        x += rnd.randrange(38, 86)
    lily = Image.open(os.path.join(OUT, "lily.png"))
    im.paste(lily, (POND_X + 28, top), lily)
    im.save(os.path.join(OUT, "yard-ground.png"))

if __name__ == "__main__":
    yard_ground()
    print("yard ground ok")
