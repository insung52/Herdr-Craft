# Pixel icons that stand for Herdr functions (original drawings, Minecraft-flavoured):
#   add machine = nether portal, remote machine = end portal frame (eye in = connected),
#   settings = crafting table, search/zoom = spyglass, restore = totem of undying,
#   command palette = command block, branch = rail, files = chest, changes = book & quill,
#   sidebar = map, sort = clock, new space = sapling, close = barrier,
#   5h limit = hunger shanks, 7d limit = hearts.
#   python gen_icons.py  -> icons/*.svg
import math, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "icons")
os.makedirs(OUT, exist_ok=True)

PAL = {
    "k": "#1a1a1a", "o": "#1b0f2e", "O": "#34205a", "p": "#7b2fd0", "P": "#b067ff", "q": "#e2c2ff",
    "e": "#dfe3ab", "E": "#b7bd7f", "f": "#2f6b5e", "F": "#3e8f7c", "y": "#47d39a", "Y": "#1f6b4a",
    "w": "#b5834f", "W": "#7a5530", "d": "#4f361f", "s": "#c8c8d0", "S": "#6b6b75",
    "r": "#c83030", "R": "#8a1c1c", "g": "#f2c93a", "G": "#b8901e", "b": "#5a8fe0", "N": "#1a2550",
    "l": "#5fb544", "L": "#2f7a24", "n": "#6b4426", "m": "#c9683f", "M": "#f0a070", "h": "#f2ecd8",
    "t": "#e9c24a", "T": "#a5832a", "v": "#3fbf3f", "x": "#c77b3d", "X": "#8a5226", "z": "#2d2d2d",
    "i": "#eeeeee", "a": "#b9b9c2", "A": "#6b6b72", "u": "#e9dfc0", "U": "#a8946a", "j": "#3b2d1f",
    "K": "#f7f7f7", "B": "#e33b3b", "H": "#e0302f", "I": "#ff9b9b", "J": "#3a2224", "Q": "#3b2a1c",
    "c": "#8e6438", "C": "#c49a63", "1": "#2f5f0a", "2": "#7fe024", "3": "#c6ff4a", "4": "#ffffd0",
}

ICONS = {
    "moon": [
        "................", "................", "............ii..", "..........iiii..",
        ".........iiAi...", ".........iii....", "........iiAi....", "........iii.....",
        "........iiAi....", "........iii.....", ".........iiAi...", ".........iiii...",
        "..........iiAi..", "............ii..", "................", "................",
    ],
    "sun": [
        "................", "................", "..gg........gg..", "..gtgg....ggtg..",
        "...gTTTTTTTTg...", "...TttttttttT...", "...TttTTTTttT...", "...TtTttttTtT...",
        "...TtTttttTtT...", "...TttTTTTttT...", "...TttttttttT...", "...gTTTTTTTTg...",
        "..gtgg....ggtg..", "..gg........gg..", "................", "................",
    ],
    "moon-old": [
        "................", "................", "...aaaaaaaaaa...", "...aiiiiiiiiAa..",
        "...aiAAiiiiiia..", "...aiAAiiiAAia..", "...aiiiiiiAAia..", "...aiiiiiiiiia..",
        "...aiiAAAiiiia..", "...aiiAAAiiiia..", "...aiiiiiiiAia..", "...aAiiiiiiiAa..",
        "...aaaaaaaaaaa..", "................", "................", "................",
    ],
    "eye-of-ender": [
        "................", "................", ".....kkkkkk.....", "....kYyyyyYk....",
        "...kYyyFFyyYk...", "..kYyyFkkFyyYk..", "..kyyFkkkkFyyk..", "..kyyFkkkkFyyk..",
        "..kyyFkkkkFyyk..", "..kYyyFkkFyyYk..", "...kYyyFFyyYk...", "....kYyyyyYk....",
        ".....kkkkkk.....", "................", "................", "................",
    ],
    "ender-pearl": [
        "................", "................", ".....kkkkkk.....", "....kfffffFk....",
        "...kfFFffffFk...", "..kfFiFfffffFk..", "..kfFFffffffFk..", "..kffffffffffk..",
        "..kffffffffFfk..", "..kFfffffffFfk..", "...kFfffffFFk...", "....kFFFFFFk....",
        ".....kkkkkk.....", "................", "................", "................",
    ],
    "end-frame": [
        "................", "................", "..ffffffffffff..", "..fFFFFyyFFFFf..",
        "..fFFFyYYyFFFf..", "..ffffyYYyffff..", "..eeeeeyyeeeee..", "..eEeeeeeeeEee..",
        "..eeeeEeeeeeee..", "..eeEeeeeeEeee..", "..eeeeeeEeeeee..", "..eEeeeeeeeeEe..",
        "..eeeeeEeeeeee..", "..EEEEEEEEEEEE..", "................", "................",
    ],
    "end-frame-empty": [
        "................", "................", "..ffffffffffff..", "..fFFFFkkFFFFf..",
        "..fFFFkkkkFFFf..", "..ffffkkkkffff..", "..eeeeeeeeeeee..", "..eEeeeeeeeEee..",
        "..eeeeEeeeeeee..", "..eeEeeeeeEeee..", "..eeeeeeEeeeee..", "..eEeeeeeeeeEe..",
        "..eeeeeEeeeeee..", "..EEEEEEEEEEEE..", "................", "................",
    ],
    "nether-portal": [
        "oooooooooooooooo", "oOOOOOOOOOOOOOOo", "oOppPppppPpppPOo", "oOpPqPppPppPqpOo",
        "oOppPppPqPppPpOo", "oOPpppPpPpppPpOo", "oOppPqppppPqppOo", "oOpPpPppPppPppOo",
        "oOppppPqPpppPpOo", "oOPpPppPppPqppOo", "oOppqPpppPpPppOo", "oOpPppPpqpppPpOo",
        "oOppPpppPppPpPOo", "oOpppPqpppppppOo", "oOOOOOOOOOOOOOOo", "oooooooooooooooo",
    ],
    "crafting-table": [
        "dddddddddddddddd", "dCCWCCCCWCCCCWCd", "dCWWWWWWWWWWWWCd", "dCCWCCCCWCCCCWCd",
        "dddddddddddddddd", "dWwwwwwwwwwwwwWd", "dWwsSwwwwwwnnwWd", "dWwsSwwwwwnnwwWd",
        "dWwsSwwwwwwnwwWd", "dWwnwwwwwwwnwwWd", "dWwnwwwwwwwnwwWd", "dWwwwwwwwwwwwwWd",
        "dWwwwwwwwwwwwwWd", "dWwwwwwwwwwwwwWd", "dWWWWWWWWWWWWWWd", "dddddddddddddddd",
    ],
    "spyglass": [
        "................", "...........kkk..", "..........kbbbk.", ".........kgbbbk.",
        "........kgGgbk..", ".......kgGgGk...", "......kgGgGk....", ".....kgGgGk.....",
        "....kaAaAk......", "...kaAaAk.......", "..kaAaAk........", ".kaAaAk.........",
        ".kAaAk..........", "..kkk...........", "................", "................",
    ],
    "chest": [
        "................", ".kkkkkkkkkkkkkk.", ".kwwwwwwwwwwwwk.", ".kwWWWWWWWWWWwk.",
        ".kwwwwwwwwwwwwk.", ".kddddddddddddk.", ".kdddddssdddddk.", ".kwwwwwsSwwwwwk.",
        ".kwwwwwwwwwwwwk.", ".kwWWWWWWWWWWwk.", ".kwwwwwwwwwwwwk.", ".kwWWWWWWWWWWwk.",
        ".kwwwwwwwwwwwwk.", ".kkkkkkkkkkkkkk.", "................", "................",
    ],
    "book-quill": [
        "............KK..", "...........KKKk.", "..........KKKk..", ".........KKKk...",
        "........KKKk....", ".kkkkkkkjkk.....", ".krrrrrjrrrk....", ".kruuuuuuurk....",
        ".kruUUUUUurk....", ".kruuuuuuurk....", ".kruUUUUuurk....", ".kruuuuuuurk....",
        ".kRRRRRRRRRk....", ".kkkkkkkkkkk....", "................", "................",
    ],
    "map": [
        "................", ".UUUUUUUUUUUUUU.", ".UuuuuuuuuuuuuU.", ".UubbbblllbbbuU.",
        ".UubbllLllbbbuU.", ".UublllllLlbbuU.", ".UubblLllllbbuU.", ".UubbbllllbbbuU.",
        ".UubbbbbllbbbuU.", ".UubbbbbbbrbbuU.", ".UubbbbbbbbbbuU.", ".UuuuuuuuuuuuuU.",
        ".UUUUUUUUUUUUUU.", "................", "................", "................",
    ],
    "clock": [
        "................", ".....kkkkkk.....", "....kgGGGGgk....", "...kgbbbbbbgk...",
        "..kgbbbtbbbbgk..", "..kGbbtttbbbGk..", "..kGbbbtbbbbGk..", "..kGllllllllGk..",
        "..kGNNNNNNNNGk..", "..kGNNqNNNNNGk..", "..kgNNNNNqNNgk..", "...kgNNNNNNgk...",
        "....kgGGGGgk....", ".....kkkkkk.....", "................", "................",
    ],
    "totem": [
        "......kkkk......", ".....kttttk.....", ".....ktvvtk.....", ".....kttttk.....",
        ".....kTTTTk.....", "..kkkktttTkkkk..", ".kttttttttttttk.", ".kTTkttttttkTTk.",
        "..kk.kvttvk.kk..", ".....ktttTk.....", ".....kTttTk.....", ".....ktTTtk.....",
        ".....kt..tk.....", ".....kk..kk.....", "................", "................",
    ],
    "command-block": [
        "kkkkkkkkkkkkkkkk", "kxxxxxxxxxxxxxxk", "kxXXxxXXxxXXxxXk", "kxxzzzzzzzzzzxxk",
        "kxxzizzzzzzzzxxk", "kxXzziizzzzzzXxk", "kxxzzziizzzzzxxk", "kxXzziizzzzzzXxk",
        "kxxziizziiiizxxk", "kxXzzzzzzzzzzXxk", "kxxxxxxxxxxxxxxk", "kxXXxxXXxxXXxxXk",
        "kxxxxxxxxxxxxxxk", "kXXXXXXXXXXXXXXk", "kkkkkkkkkkkkkkkk", "................",
    ],
    "rail": [
        "...a........a...", ".nnAnnnnnnnnAnn.", "...a........a...", "...a........a...",
        ".nnAnnnnnnnnAnn.", "...a........a...", "...a........a...", ".nnAnnnnnnnnAnn.",
        "...a........a...", "...a........a...", ".nnAnnnnnnnnAnn.", "...a........a...",
        "...a........a...", ".nnAnnnnnnnnAnn.", "...a........a...", "...a........a...",
    ],
    "sapling": [
        "................", "......l..l......", ".....lLl.lL.....", "....lLlLlLlL....",
        "...lLllLlllLl...", "....lLlnlLl.....", "......lnl.......", ".......n........",
        "...l...n...l....", "..lLl..n..lLl...", "...lLl.n.lLl....", ".....llnll......",
        ".......n........", ".......n........", "................", "................",
    ],
    "grass-block": [
        "llLllLllllLlllLl", "lLlllllLlLllllll", "LllLLllllllLLlLl", "nlnlLlnlnLlnlnll",
        "nnmnnnwnnnnnnwnn", "nwnnnnnnwnnnmnwn", "nnnnwnnnnnwnnnnn", "Wnwnnnnmnnnnwnnn",
        "nnnmnwnnnnWnnnnw", "wnnnnnnnwnnnnmnn", "nnWnnwnnnnnwnnnn", "nnnwnnnmnnnnWnwn",
        "Wnnnnnwnnnwnnnnn", "nnwnmnnnWnnnnwnW", "nnnnnnnwnnnnmnnn", "WnnwnnWnnnnwnnnn",
    ],
}

# HUD pips in the game's style: black outline, highlight top-left; an empty one keeps the outline
# with a dark grey inside. Hearts = health, shanks (meat up-left, bone down-right) = hunger.
HEART = [".kkk.kkk.", "kWRRkRRRk", "kRRRRRRRk", "kRRRRRRDk", ".kRRRRDk.", "..kRRDk..", "...kDk...", "....k...."]
SHANK = ["..kkk....", ".kRrrk...", "kRWRbbk..", "kRRbbbbk.", ".kbbbBbk.", "..kbBBkk.", "...kkkhk.", ".....khhk", "......kk."]
XP = ["...oooo...", ".ooggggoo.", ".ogGGGGgo.", "ogGGllGGgo", "ogGlcclGgo", "ogGlcclGgo", "ogGGllGGgo", ".ogGGGGgo.", ".ooggggoo.", "...oooo..."]

def variant(rows, fill, empty, split=None):
    out = []
    for r in rows:
        s = ""
        for i, ch in enumerate(r):
            if ch in fill and (split is None or i >= split):
                ch = empty
            s += ch
        out.append(s)
    return out

def barrier():
    rows = []
    for y in range(16):
        r = ""
        for x in range(16):
            dx, dy = x - 7.5, y - 7.5
            d = math.hypot(dx, dy)
            r += "B" if 5.0 <= d <= 7.2 or (d < 5.6 and abs(dx + dy) <= 1.1) else "."
        rows.append(r)
    return rows

def save_svg(name, rows):
    w, h = len(rows[0]), len(rows)
    for r in rows:
        assert len(r) == w, (name, r)
    rects = []
    for y, r in enumerate(rows):
        x = 0
        while x < w:
            ch = r[x]
            if ch == ".":
                x += 1; continue
            n = 1
            while x + n < w and r[x + n] == ch:
                n += 1
            rects.append(f'<rect x="{x}" y="{y}" width="{n}" height="1" fill="{PAL[ch]}"/>')
            x += n
    with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w * 4}" height="{h * 4}" '
                f'shape-rendering="crispEdges">' + "".join(rects) + "</svg>\n")

if __name__ == "__main__":
    for k, rows in ICONS.items():
        save_svg(k, rows)
    save_svg("barrier", barrier())
    hp = {"k": "#000000", "R": "#ff1a1a", "D": "#b80e0e", "W": "#ffb8b8"}
    sp = {"k": "#000000", "R": "#c81e1e", "r": "#e64040", "W": "#f4c8b8", "b": "#b07040", "B": "#7a4a22", "h": "#f0e6c8"}
    EMPTY = "#2b2b2b"
    def colored(rows, pal, empty_from=None, empty_all=False, line="#000000"):
        out = []
        for r in rows:
            out.append([(None if ch == "." else (line if ch == "k" else (EMPTY if empty_all or (empty_from is not None and i < empty_from) else pal[ch]))) for i, ch in enumerate(r)])
        return out
    def save_c(name, grid):
        w, h = len(grid[0]), len(grid); rects = []
        for y, row in enumerate(grid):
            for x, c in enumerate(row):
                if c: rects.append(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{c}"/>')
        with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as f:
            f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w * 4}" height="{h * 4}" shape-rendering="crispEdges">' + "".join(rects) + "</svg>\n")
    save_c("heart", colored(HEART, hp))
    save_c("heart-half", [[(EMPTY if (c and c != "#000000" and i >= 5) else c) for i, c in enumerate(r)] for r in colored(HEART, hp)])
    save_c("heart-empty", colored(HEART, hp, empty_all=True))
    save_c("shank", colored(SHANK, sp))
    save_c("shank-half", colored(SHANK, sp, empty_from=4))
    save_c("shank-empty", colored(SHANK, sp, empty_all=True))
    # regeneration flash: white outline, brighter body
    hp_hl = {"k": "#ffffff", "R": "#ff5a5a", "D": "#e02a2a", "W": "#ffffff"}
    sp_hl = {"k": "#ffffff", "R": "#ff4a4a", "r": "#ff7a7a", "W": "#ffffff", "b": "#d89058", "B": "#a86a34", "h": "#ffffff"}
    save_c("heart-hl", colored(HEART, hp_hl, line="#ffffff"))
    save_c("shank-hl", colored(SHANK, sp_hl, line="#ffffff"))
    # poisoned heart (yellow-green) and the hunger effect's green shank
    hp_po = {"k": "#000000", "R": "#a8b528", "D": "#6f7a12", "W": "#e6f08a"}
    sp_po = {"k": "#000000", "R": "#6b8f2a", "r": "#86a83a", "W": "#c8e08a", "b": "#7a8a3a", "B": "#4f5a22", "h": "#d8e0b0"}
    save_c("heart-poison", colored(HEART, hp_po))
    save_c("heart-half-poison", [[(EMPTY if (c and c != "#000000" and i >= 5) else c) for i, c in enumerate(r)] for r in colored(HEART, hp_po)])
    save_c("shank-poison", colored(SHANK, sp_po))
    save_c("shank-half-poison", colored(SHANK, sp_po, empty_from=4))
    xp = {"o": "#1b6b14", "g": "#2a9a1e", "G": "#3cc42c", "l": "#7ef05a", "c": "#2e8a22"}
    save_c("xp", colored(XP, xp))
    print("ok", len(os.listdir(OUT)))

# ── XP bar (182 x 5, shown at 2x): rounded ends, a dark track split into segments,
# and a bright-green fill whose middle row glows. Own drawing after the game's layout.
def xp_bar():
    from PIL import Image
    W, H = 182, 5
    def hx(h): return tuple(int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
    bg = Image.new("RGBA", (W, H), (0, 0, 0, 0)); fill = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    seed = 12345
    def rnd():
        nonlocal seed
        seed = (seed * 1103515245 + 12345) & 0x7fffffff
        return seed / 0x7fffffff
    for x in range(W):
        for y in range(H):
            corner = (x in (0, W - 1)) and y in (0, H - 1)
            if corner: continue
            edge = y in (0, H - 1) or x in (0, W - 1)
            seg = (x - 1) % 10            # 9 px segment + 1 px notch
            if edge:
                bg.putpixel((x, y), hx("#0a120d")); fill.putpixel((x, y), hx("#0c2412" if rnd() < 0.6 else "#173a1d")); continue
            if seg == 9:
                bg.putpixel((x, y), hx("#151f19")); fill.putpixel((x, y), hx("#4f7d2b")); continue
            end = seg in (0, 8)
            if y == 2:
                bg.putpixel((x, y), hx("#222d27" if end else "#1a241e"))
                fill.putpixel((x, y), hx(["#8fce5c", "#9fda71", "#b4f57e", "#88c657"][int(rnd() * 4)]))
            else:
                bg.putpixel((x, y), hx("#36433c" if end else "#2a3630"))
                fill.putpixel((x, y), hx(["#5f9a34", "#6aa83e", "#56892f"][int(rnd() * 3)] if y == 1 else ["#4c7a28", "#456f24", "#527f2c"][int(rnd() * 3)]))
    bg.save(os.path.join(OUT, "xpbar-bg.png")); fill.save(os.path.join(OUT, "xpbar-fill.png"))

if __name__ == "__main__":
    xp_bar()
    print("xp bar ok")

# ── ender pearl and nether portal, redrawn after the game's look (own drawings) ──
def pearl_and_portal():
    import math
    def hx(h): return h if h.startswith("#") else "#" + h
    # ender pearl: octagonal teal orb, dark rim, big dark core, light arcs up-left and down-right
    g = [[None] * 16 for _ in range(16)]
    cx = cy = 7.5
    for y in range(16):
        for x in range(16):
            dx, dy = x - cx, y - cy
            r = max(abs(dx), abs(dy)) * 0.55 + math.hypot(dx, dy) * 0.5     # octagon-ish
            if r > 7.4: continue
            a = math.degrees(math.atan2(dy, dx))
            if r > 6.5: c = "#0a3832"
            elif r > 5.6: c = "#11594d"
            elif r > 3.6: c = "#1f7f6b"
            elif r > 2.6: c = "#145f52"
            else: c = "#05241f"
            if 4.0 < r <= 5.6 and -165 < a < -100: c = "#7ae6cc"      # up-left highlight arc
            elif 4.0 < r <= 5.6 and (-180 <= a <= -165 or -100 <= a < -85): c = "#3fae95"
            if 4.0 < r <= 5.6 and 15 < a < 70: c = "#5fd5bb"          # down-right highlight arc
            g[y][x] = c
    rects = "".join(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{g[y][x]}"/>' for y in range(16) for x in range(16) if g[y][x])
    with open(os.path.join(OUT, "ender-pearl.svg"), "w", encoding="utf-8") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="64" height="64" shape-rendering="crispEdges">{rects}</svg>\n')
    # nether portal in an obsidian frame: diamond rings swirling round the middle, bright flecks
    obs = ["#0f0c18", "#15111f", "#1c1529", "#2a2140", "#3a2d56"]
    ring = ["#3a0a8a", "#5414b4", "#6b22d4", "#8a3df0", "#6b22d4", "#5414b4"]
    seed = 7
    def rnd():
        nonlocal seed
        seed = (seed * 1103515245 + 12345) & 0x7fffffff
        return seed / 0x7fffffff
    rects = []
    for y in range(16):
        for x in range(16):
            if x < 2 or x > 13 or y < 2 or y > 13:
                v = rnd(); c = obs[0] if v < 0.45 else obs[1] if v < 0.7 else obs[2] if v < 0.86 else obs[3] if v < 0.95 else obs[4]
            else:
                dx, dy = x - 7.5, y - 7.5
                d = abs(dx) + abs(dy) + 0.9 * math.sin(math.atan2(dy, dx) * 2)   # a twist in the rings
                c = ring[int(d) % len(ring)]
                if rnd() < 0.03: c = "#b070ff"
                if rnd() < 0.02: c = "#2c0866"
            rects.append(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{c}"/>')
    with open(os.path.join(OUT, "nether-portal.svg"), "w", encoding="utf-8") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="64" height="64" shape-rendering="crispEdges">{"".join(rects)}</svg>\n')

if __name__ == "__main__":
    pearl_and_portal()
    print("pearl + portal ok")
