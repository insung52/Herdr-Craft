# Generates the Minecraft-style pixel art for the mc-* mods (all hand-drawn here, no game assets).
#   python gen_art.py         -> writes *.gif (animated sprites) and *.svg (static icons) next to this file
# Sprites are drawn as character grids; each letter is one pixel colour from PAL.
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SCALE = 2  # 2 screen px per sprite px: shown at natural size so it stays crisp at 100% display scale

PAL = {
    "O": "#e3893b",  # ginger fur
    "D": "#b35a25",  # stripe
    "L": "#f6d3a0",  # cream belly/muzzle
    "K": "#2a1a12",  # dark (closed eyes, paws outline)
    "G": "#5fd35a",  # green eye
    "P": "#ee8fa6",  # pink nose
    "W": "#f2f5ff",  # white (z)
    "B": "#8fc7ff",  # pale blue (z shadow)
    "R": "#d63b3b",  # gift red
    "r": "#9e2424",  # gift red shadow
    "Y": "#ffd84a",  # ribbon gold
    "E": "#7cf06a",  # xp green
    "e": "#c9ff6a",  # xp yellow-green
    "s": "#ffffff",  # sparkle
    # icons
    "g": "#5aa83a", "h": "#7ccd4c", "d": "#8a5a32", "n": "#6b4426", "c": "#a57444",
    "x": "#3a3a46", "X": "#20202a", "i": "#b8ecff", "j": "#6fd6ff", "q": "#3fb7e8",
    "v": "#2e1052", "u": "#7b2fd0", "U": "#b067ff", "w": "#e2c2ff", "o": "#16082a",
    "t": "#ffb02e", "T": "#ffe58a", "f": "#8a8a96", "F": "#c9c9d6", "k": "#5c3a1e",
    "m": "#c03030", "M": "#e0e0e8", "a": "#9b9ba8", "A": "#5e5e6a",
}

def grid(rows, w=None):
    w = w or max(len(r) for r in rows)
    out = [r.ljust(w, ".") for r in rows]
    for r in out:
        assert len(r) == w, (len(r), r)
    return out

# ── cat, side view, running right (18 x 10) ─────────────────────────────────────
HEAD_BODY = [
    "............OO..OO",
    ".O..........OOOOOO",
    ".O..........OGOOGO",
    ".O..........OLPPLO",
    "..OOODDOODDOOLLLLO",
    "..OOOOOOOOOOOOOOO.",
    "..OODDOODDOOOOOO..",
    "..LLLLLLLLLLLLLL..",
]
LEGS = [
    ["..O.O........O.O..", ".K.K..........K.K."],   # stretched
    ["...OO.......OO....", "...KK.......KK...."],   # passing
    ["....O.O...O.O.....", ".....K.K.K.K......"],   # gathered
    ["...OO.......OO....", "...KK.......KK...."],   # passing
]
def run_frame(i):
    body = HEAD_BODY + LEGS[i]
    if i in (1, 3):                      # bob up one pixel on the passing frames
        body = body[1:] + ["." * 18]
    tail_up = i in (0, 2)
    rows = [list(r) for r in body]
    if not tail_up:                      # tail swings: lower it one pixel
        for r in range(0, 3):
            rows[r][1] = "."
        rows[1][0] = "O"; rows[2][0] = "O"; rows[3][1] = "O"
    return grid(["".join(r) for r in rows], 18)
RUN = [run_frame(i) for i in range(4)]

# ── cat, curled asleep (18 x 10), two breaths with a drifting z ─────────────────
SLEEP_BASE = [
    "..................",
    "..................",
    "..................",
    "..........OO..OO..",
    "..........OOOOOO..",
    "...OODDOODOKKOKKO.",
    "..OOOOOOOOOLLPLLO.",
    "..ODDOODDOOLLLLLO.",
    ".LLLLLLLLLLLLLLLL.",
    "OOOOOO............",
]
def sleep_frame(i):
    rows = [list(r) for r in SLEEP_BASE]
    if i == 1:  # breathe: back rises
        rows[4][3:9] = list("OODDOO")
    if i == 0:
        rows[2][16] = "W"
    else:
        rows[0][16] = "W"; rows[0][17] = "W"; rows[1][17] = "B"
    return grid(["".join(r) for r in rows], 18)
SLEEP = [sleep_frame(i) for i in range(2)]

# ── cat sitting, front view, holding a gift (14 x 13) ───────────────────────────
SIT_HEAD = [
    "...OO....OO...",
    "...OOOOOOOO...",
    "...OGKOOGKO...",
    "...OOLPPLOO...",
    "...OLLLLLLO...",
    "....OOOOOO....",
]
GIFT = [
    "...RRRYRRRR...",
    "...YYYYYYYY...",
    "...RRRYRRRR...",
    "...rrrYrrrr...",
]
def gift_frame(i):
    head = SIT_HEAD if i == 0 else ["." * 14] + SIT_HEAD[:-1]
    bow = ["....Y..Y......", ".....YY......."]
    body = [
        "..OOOOOOOOOO..",
        "..OODOOOODOO..",
    ]
    rows = head + bow[:1] + bow[1:] if False else head
    rows = rows + ([".....YYY......"] if i == 0 else ["....Y.Y.Y....."]) + GIFT + ["..KK......KK.."]
    return grid(rows, 14)
GIFT_FR = [gift_frame(i) for i in range(2)]

# ── cat sitting, happy eyes, xp orb bobbing above (14 x 13): "done" ─────────────
def done_frame(i):
    orb = [
        "......Ee......",
        ".....EeeE.....",
        "......EE......",
    ]
    blank = ["." * 14]
    head = [
        "...OO....OO...",
        "...OOOOOOOO...",
        "...OKOOOOKO...",   # ^ ^ happy eyes (closed curves)
        "...KOKPPKOK...",
        "...OLLLLLLO...",
        "....OOOOOO....",
    ]
    body = [
        "..OOOOOOOOOO..",
        "..OODLLLLDOO..",
        "..OOOLLLLOOO..",
        "..KK......KK..",
    ]
    top = (orb + blank) if i == 0 else (blank + orb)
    if i == 1:
        top[0] = "..s.........."
    return grid(top + head + body, 14)
DONE = [done_frame(i) for i in range(2)]

# ── static icons (16 x 16) ──────────────────────────────────────────────────────
ICONS = {
    "grass": [
        "gghgghgghgghgghg", "hgghhgghgghhgghg", "ggghgghggghgghgg", "dgdgggdgdggdgdgg",
        "ddndddcdddnddcdd", "dcdddnddcdddndcd", "ddddcdddddcdddnd", "ndcddddnddddcddd",
        "dddndcddddnddddc", "cdddddddcdddndcd", "ddnddcdddddcdddd", "dddcdddnddddndcd",
        "ndddddcdddcddddd", "ddcdndddndddcdnd", "dddddddcddddddcd", "ncdddnddddcdnddd",
    ],
    "beacon": [
        "......jijj......", "......jiij......", ".....qjiijq.....", "XXXXXXXXXXXXXXXX",
        "XiiiiiiiiiiiiiiX", "XijjjjjjjjjjjjiX", "XjjqqqqqqqqqqjjX", "Xjjq..iiii..qjjX",
        "Xjjq.iWWWWi.qjjX", "Xjjq.iWWWWi.qjjX", "Xjjq..iiii..qjjX", "XjjqqqqqqqqqqjjX",
        "XxxxxxxxxxxxxxxX", "XxAxxAxxAxxAxxAX", "XxxxxxxxxxxxxxxX", "XXXXXXXXXXXXXXXX",
    ],
    "portal": [
        "oooooooooooooooo", "oovvvvvvvvvvvvoo", "ovuuUuuuuUuuuuvo", "ovuUwUuuUuuUwuvo",
        "ovuuUuuUwUuuUuvo", "ovUuuuUuUuuuuUvo", "ovuuUwuuuuUwuuvo", "ovuUuUuuUuuUuuvo",
        "ovuuuuUwUuuuUuvo", "ovUuUuuUuuUwuuvo", "ovuuwUuuuUuUuuvo", "ovuUuuUuwuuuUuvo",
        "ovuuUuuuUuuUuUvo", "ovuuuUwuuuuuuuvo", "oovvvvvvvvvvvvoo", "oooooooooooooooo",
    ],
    "pickaxe": [
        "................", "...iiiiiiii.....", "..ijjjjjjjjiq...", ".ijq......qjjq..",
        ".jq.......kqjq..", "..........k.qjq.", ".........k...qj.", "........k.....j.",
        ".......k........", "......k.........", ".....k..........", "....k...........",
        "...k............", "..k.............", ".k..............", "................",
    ],
    "compass": [
        "................", ".....AAAAAA.....", "....AaMMMMaA....", "...AaMMMMMMaA...",
        "..AaMMMmmMMMaA..", "..AMMMMmmMMMMA..", "..AMMMMmmMMMMA..", "..AMMMMXXMMMMA..",
        "..AMMMMffMMMMA..", "..AMMMMffMMMMA..", "..AaMMMffMMMaA..", "...AaMMMMMMaA...",
        "....AaMMMMaA....", ".....AAAAAA.....", "................", "................",
    ],
    "torch": [
        "................", ".......TT.......", "......TttT......", "......tTTt......",
        ".......tt.......", ".......kk.......", ".......kn.......", ".......kn.......",
        ".......kn.......", ".......kn.......", ".......kn.......", ".......kn.......",
        ".......kn.......", ".......kn.......", ".......nn.......", "................",
    ],
    "cat": None,  # filled below from the sitting cat head
    "house": [
        ".......mm.......", "......mmmm......", ".....mmMMmm.....", "....mmmmmmmm....",
        "...mmmmmmmmmm...", "..mmmmmmmmmmmm..", ".mmmmmmmmmmmmmm.", "..cccccccccccc..",
        "..cnnnccccnnnc..", "..cnjnccccnjnc..", "..cnnnckkcnnnc..", "..cccccktkcccc..",
        "..cccccknkcccc..", "..cnccckkkcncc..", "..cccccknkcccc..", "..nnnnnnnnnnnn..",
    ],
    "gift": [
        "................", "................", "....Y.....Y.....", ".....Y...Y......",
        "......YYY.......", "..RRRRRYRRRRRR..", "..RRRRRYRRRRRR..", "..YYYYYYYYYYYY..",
        "..RRRRRYRRRRRR..", "..RRRRRYRRRRRR..", "..RRRRRYRRRRRR..", "..rrrrrYrrrrrr..",
        "..rrrrrYrrrrrr..", "................", "................", "................",
    ],
    "xp": [
        "................", "................", "................", "................",
        "......EEEE......", ".....EeeeeE.....", "....EesseeeE....", "....EeseeeeE....",
        "....EeeeeeeE....", "....EEeeeeEE....", ".....EEeeEE.....", "......EEEE......",
        "................", "................", "................", "................",
    ],
    "bed": [
        "................", "................", "................", "................",
        "................", "................", "MMMM............", "MMMMmmmmmmmmmmmm",
        "MMMMmmmmmmmmmmmm", "ccccmrmmmmrmmmmm", "nccccccccccccccn", "nccccccccccccccn",
        "n..............n", "................", "................", "................",
    ],
}
# the pickaxe handle uses 'k' / head 'i','j','q' — fine as drawn above.
ICONS["cat"] = grid(["." * 14] + SIT_HEAD + [
    "..OOOOOOOOOO..", "..OODLLLLDOO..", "..OOOLLLLOOO..", "..OOOLLLLOOO..", "..KK......KK..",
] + ["." * 14] * 4, 14)[:16]


def rgba(ch):
    if ch == ".":
        return (0, 0, 0, 0)
    h = PAL[ch].lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)


def to_image(rows, scale=SCALE):
    w, h = len(rows[0]), len(rows)
    im = Image.new("RGBA", (w * scale, h * scale), (0, 0, 0, 0))
    px = im.load()
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            c = rgba(ch)
            if c[3] == 0:
                continue
            for dy in range(scale):
                for dx in range(scale):
                    px[x * scale + dx, y * scale + dy] = c
    return im


def flip(rows):
    return [r[::-1] for r in rows]


PATROL_W = 70  # sprite px the cat runs back and forth across


def patrol_frames(phase=0.0, step=2):
    """The cat runs right across PATROL_W, turns, runs back: the whole trip baked into one gif."""
    h = len(RUN[0]) + 1
    xs = list(range(0, PATROL_W - 18 + 1, step))
    path = [(x, False) for x in xs] + [(x, True) for x in reversed(xs)]
    out = []
    for i, (x, back) in enumerate(path):
        fr = RUN[i % 4]
        fr = flip(fr) if back else fr
        canvas = [["."] * PATROL_W for _ in range(h)]
        for y, r in enumerate(fr):
            for dx, ch in enumerate(r):
                if ch != ".":
                    canvas[y + 1][x + dx] = ch
        out.append(["".join(r) for r in canvas])
    k = int(len(out) * phase)
    return out[k:] + out[:k]


def save_gif(name, frames, ms):
    ims = [to_image(f) for f in frames]
    # single shared palette with index 255 as transparency
    pal_ims = []
    for im in ims:
        p = im.convert("RGB").convert("P", palette=Image.ADAPTIVE, colors=255)
        mask = im.getchannel("A").point(lambda a: 255 if a < 128 else 0)
        p.paste(255, mask=mask)
        p.info["transparency"] = 255
        pal_ims.append(p)
    pal_ims[0].save(os.path.join(HERE, name), save_all=True, append_images=pal_ims[1:],
                    duration=ms, loop=0, disposal=2, transparency=255, optimize=False)
    # first frame also as PNG (static fallback / list thumbnails)
    ims[0].save(os.path.join(HERE, name.replace(".gif", ".png")))


def save_svg(name, rows):
    w, h = len(rows[0]), len(rows)
    rects = []
    for y, r in enumerate(rows):
        x = 0
        while x < w:
            ch = r[x]
            if ch == ".":
                x += 1
                continue
            run = 1
            while x + run < w and r[x + run] == ch:
                run += 1
            rects.append(f'<rect x="{x}" y="{y}" width="{run}" height="1" fill="{PAL[ch]}"/>')
            x += run
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w * 4}" height="{h * 4}" '
           f'shape-rendering="crispEdges">' + "".join(rects) + "</svg>\n")
    with open(os.path.join(HERE, name), "w", encoding="utf-8") as f:
        f.write(svg)


if __name__ == "__main__":
    # cats are drawn by gen_cats.py now; this script only makes the static icons
    for k, rows in ICONS.items():
        if k != "cat":
            save_svg(f"{k}.svg", grid(rows))
    print("ok")
