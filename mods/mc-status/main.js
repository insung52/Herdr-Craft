// mc-status: the Minecraft "front yard" bottom bar (a copy of my-status with a new look).
// Logic kept as-is from my-status; only the look changed.
// my-status: the bottom bar. A copy of Herdr's workspace-status plus
//  - Claude 5h / 7d limits, read from the `cc.*` labels that ~/.claude/statusline.js puts on each
//    terminal (this computer's and every connected machine's), newest observation wins;
//  - a "↻ 복구" button and the restore logic that used to live in the claude-restore mod:
//    once per boot, a snapshot every 2 minutes, and on click. Safe to click any time (the script
//    only touches tabs with no agent, skips running sessions, and a mutex stops overlaps).
import { View, div, svg, image } from "gpui-kit";
import { h_flex, v_flex } from "gpui-base";
import { META } from "./art/cats8/meta.js";
import { spaces, agents, terminals, theme, run, window, keys, exec, hc, appHome, readTextFile, writeTextFile, notify, checking, layout, settings, shared, focused } from "herdr";

const PS = "pwsh";
const SNAPSHOT_MS = 120000;
// The restore/restart scripts live on the Windows PC. A Herdr window on another OS (the MacBook)
// runs them on that PC through its machine entry instead of locally.
const IS_WIN = /^[A-Za-z]:/.test(appHome());
const PC = "desktop";
function psRun(name, scriptArgs, opts) {
  if (IS_WIN) return exec(PS, ["-NoProfile", "-File", `${appHome()}/data/claude-restore/${name}`, ...scriptArgs], opts);
  // this computer's own restore on a Mac: the python twin of herdr-restore.ps1
  if (name === "herdr-restore.ps1") return exec("/bin/zsh", ["-lc", `python3 "${appHome()}/data/claude-restore/herdr-restore.py" --mode ${scriptArgs[1]}`], opts);
  const a = scriptArgs.map((x) => (/^[\w.-]+$/.test(String(x)) ? String(x) : `"${String(x).replace(/"/g, "")}"`)).join(" ");
  return exec(PS, ["-NoProfile", "-Command", `& ~\\.config\\herdr-app\\data\\claude-restore\\${name} ${a}`], { ...opts, on: PC });
}
const script = () => `${appHome()}/data/claude-restore/herdr-restore.ps1`;
// ── restart outdated sessions (per machine) — logic copied unchanged from my-status ──
const restartScript = () => `${appHome()}/data/claude-restore/herdr-restart.ps1`;
const machineOf = (t) => (String(t.address ?? "").includes("/") ? String(t.address).split("/")[0] : "");
const machineLabel = (m) => (m === "" ? "이 PC" : m);

async function installedVersion(machine) {
  const r = await exec("claude", ["--version"], machine ? { on: machine, timeout: 30000 } : { timeout: 30000 }).catch(() => null);
  const m = /(\d+\.\d+\.\d+)/.exec(r?.stdout ?? "");
  return m ? m[1] : "";
}

async function runRestartScript(machine) {
  // from the Mac, the PC itself is the machine "desktop" = "this computer" for the script
  const sm = IS_WIN ? machine : machine === PC ? "" : machine;
  if (!IS_WIN && machine === "") return { res: { restarted: [], skipped: ["this Mac has no restart script"], busy: false }, err: "" };
  const r = await psRun("herdr-restart.ps1", sm ? ["-Machine", sm] : [], { timeout: 600000 });
  const m = /RESULT (\{.*\})/.exec(r.stdout ?? "");
  let res = null;
  try { res = m ? JSON.parse(m[1]) : null; } catch {}
  return { res, err: r.stderr };
}
const bootFile = () => `${appHome()}/data/claude-restore/last-boot.txt`;

// Each agent keeps one cat coat everywhere (list, tabs, pane header, yard): picked from its address.
const COATS = ["ginger", "tuxedo", "black", "calico", "siamese", "gray", "white"];
const coatOf = (addr) => { let h = 0; for (const ch of String(addr ?? "")) h = (h * 31 + ch.charCodeAt(0)) >>> 0; return COATS[h % COATS.length]; };
const CATS = "mods/mc-status/art/cats8";
const ICONS = "mods/mc-status/art/icons";

// ── limits ────────────────────────────────────────────────────────
const lerp = (a, b, t) => a.map((v, i) => Math.round(v + (b[i] - v) * t));
const clamp = (x, lo, hi) => Math.min(Math.max(x, lo), hi);
const GREEN = [166, 227, 161], YELLOW = [249, 226, 175], RED = [243, 139, 168];
const hex = (c) => "#" + c.map((v) => v.toString(16).padStart(2, "0")).join("");
const gradient = (x) => { x = clamp(x, 0, 1); return x < 0.5 ? lerp(GREEN, YELLOW, x / 0.5) : lerp(YELLOW, RED, (x - 0.5) / 0.5); };

// pace = used% / elapsed% of the window: ≤0.6 green, 1.05 yellow, ≥1.5 red; ≥95% always red.
function limitColor(used, resetsAt, periodSec) {
  if (used >= 95) return hex(RED);
  const remaining = clamp((resetsAt - Date.now()) / 1000, 0, periodSec);
  const elapsed = Math.max(1 - remaining / periodSec, 0.1);
  return hex(gradient(clamp((used / 100 / elapsed - 0.6) / 0.9, 0, 1)));
}

// Which band the pace is in: "good" (green, well under pace), "bad" (red, ahead of pace or >=95%), else "ok".
function paceZone(used, resetsAt, periodSec) {
  if (used >= 95) return { zone: "bad", sev: 1 };
  const remaining = clamp((resetsAt - Date.now()) / 1000, 0, periodSec);
  const elapsed = Math.max(1 - remaining / periodSec, 0.1);
  const x = clamp((used / 100 / elapsed - 0.6) / 0.9, 0, 1);
  // good: strength 0 at the edge of the green band (x=0.25) -> 1 at x=0 (pace <= 0.6)
  // bad:  sev 0.3 at the edge of the red band (x=0.75) -> 1 at x=1 (pace >= 1.5)
  return x < 0.25 ? { zone: "good", sev: 1 - x / 0.25 } : x > 0.75 ? { zone: "bad", sev: 0.3 + 0.7 * (x - 0.75) / 0.25 } : { zone: "ok", sev: 0 };
}

function fmtLeft(resetsAt) {
  let m = Math.max(0, Math.round((resetsAt - Date.now()) / 60000));
  const dd = Math.floor(m / 1440); m -= dd * 1440;
  const hh = Math.floor(m / 60); m -= hh * 60;
  return dd ? `${dd}d${hh}h` : hh ? `${hh}h${String(m).padStart(2, "0")}m` : `${m}m`;
}

// The freshest unexpired observation of one window across every terminal's labels.
function readLimit(key) {
  const now = Date.now();
  let best = null;
  for (const t of terminals()) {
    const l = t.labels ?? {};
    const m = /^(\d+)@(\d+)$/.exec(l[key] ?? "");
    if (!m) continue;
    const resets = Number(m[2]);
    const used = Number(m[1]);
    if (resets <= now) continue;
    // A later reset means a newer window; inside one window usage only grows, so the larger
    // value is the more recent one (idle sessions keep reporting a stale smaller value).
    if (!best || resets > best.resets || (resets === best.resets && used > best.used)) best = { used, resets };
  }
  return best;
}

// ── restore ───────────────────────────────────────────────────────
async function runScript(mode) {
  const r = await psRun("herdr-restore.ps1", ["-Mode", mode], { timeout: 120000 });
  const m = /RESULT (\{.*\})/.exec(r.stdout ?? "");
  let res = null;
  try { res = m ? JSON.parse(m[1]) : null; } catch {}
  return { code: r.code, res, err: r.stderr };
}

async function bootId() {
  if (!IS_WIN) { const b = await exec("/bin/sh", ["-c", "sysctl -n kern.boottime"]).catch(() => null); return b?.code === 0 ? b.stdout.trim() : ""; }
  const r = await exec(PS, ["-NoProfile", "-Command",
    "(Get-CimInstance Win32_OperatingSystem).LastBootUpTime.ToUniversalTime().ToString('o')"]).catch(() => null);
  return r?.code === 0 ? r.stdout.trim() : "";
}

function report(out, manual) {
  if (!out.res) {
    notify({ title: "Claude restore failed", body: (out.err || "no result").slice(0, 200), level: "warning", timeout: 15000 });
    return;
  }
  if (out.res.busy) { if (manual) notify({ title: "Claude restore", body: "already running", timeout: 4000 }); return; }
  const n = (out.res.resumed ?? []).length;
  if (n > 0) notify({ title: `Claude restore: ${n} session${n === 1 ? "" : "s"} reopened`,
                      body: out.res.resumed.map((k) => k.split("/").pop()).join(" · "), timeout: 12000 });
  else if (manual) notify({ title: "Claude restore", body: "nothing to restore", timeout: 4000 });
}

export default class McStatus extends View {
  init(_props, cx) {
    this.busy = false;
    this.label = "↻ 복구";
    this.since = new Map();
    this.menuOpen = false;
    this.versions = {};       // machine ("" = this computer) -> installed claude version
    this.armed = null;        // machine whose restart button was clicked once (waiting for a confirming click)
    this.restarting = {};     // machine -> true while the script runs
    if (checking()) return;                       // herdr-app check: no snapshots, no boot restore
    cx.timer.every(300000, (cx) => { cx.spawn(async (cx) => { await this.refreshVersions(cx); }); });
    cx.spawn(async (cx) => { await cx.sleep(3000); await this.refreshVersions(cx); });
    cx.timer.every(30000, (cx) => { if (window()?.visible !== false) cx.notify(); });   // countdowns
    // The yard's one animation clock: this app shows only a GIF's first frame, so the cats are
    // frame strips stepped here. 4 fps, and only while the window is visible and a cat is out.
    this.tickN = 0;
    // 100 ms while a cat runs or a health/hunger effect shows; otherwise every 4th tick (400 ms)
    cx.timer.every(100, (cx) => {
      if (!(this.catsOut || this.hudLive) || window()?.visible === false) return;
      if (!this.fast && this.tickN++ % 4) return;
      this.animOnly = true;
      // the animation clock: advances by exactly one tick per redraw, so every frame stays on
      // screen for the same time (wall-clock time drifted against the timer and made some short)
      this.vclock = (this.vclock ?? 0) + (this.fast ? 100 : 400);
      cx.notify();
    });
    cx.timer.every(SNAPSHOT_MS, (cx) => { if (!this.busy) cx.spawn(async () => { await runScript("snapshot").catch(() => null); }); });
    cx.spawn(async (cx) => {
      const boot = await bootId();
      if (!boot) return;
      const prev = await readTextFile(bootFile()).catch(() => null);
      if (prev && prev.trim() === boot) return;          // already handled this boot
      for (let i = 0; i < 60; i++) {                     // wait for herdr-core to bring terminals back
        const r = await hc(["ls", "--json"]).catch(() => null);
        let n = 0;
        try { n = JSON.parse(r.stdout).terminals.filter((t) => t.state === "live").length; } catch {}
        if (n > 0) break;
        await cx.sleep(2000);
      }
      await cx.sleep(4000);                               // let the shells come up
      await writeTextFile(bootFile(), boot, prev ?? null).catch(() => null);
      await this.runRestore(cx, false);
    });
  }

  machines() {
    const set = new Set([""]);
    for (const t of terminals()) set.add(machineOf(t));
    if (!IS_WIN) set.delete("");                      // the Mac itself has no Claude restart script
    return [...set];
  }

  async refreshVersions(cx) {
    for (const m of this.machines()) {
      const v = await installedVersion(m);
      if (v) this.versions[m] = v;
    }
    cx.notify();
  }

  // Live Claude sessions on a machine whose reported version (label cc.ver) differs from the installed one.
  outdated(m) {
    const inst = this.versions[m];
    if (!inst) return 0;
    return terminals().filter((t) => machineOf(t) === m && t.state === "live" && t.labels?.["cc.ver"] && t.labels["cc.ver"] !== inst).length;
  }

  // First click arms the button (5 s), the second runs the restart for that machine.
  clickRestart(cx, m) {
    if (this.restarting[m]) return;
    if (this.armed !== m) {
      this.armed = m; cx.notify();
      cx.spawn(async (cx) => { await cx.sleep(5000); if (this.armed === m) { this.armed = null; cx.notify(); } });
      return;
    }
    this.armed = null;
    this.restarting[m] = true; cx.notify();
    cx.spawn(async (cx) => { await this.runRestart(cx, m); });
  }

  async runRestart(cx, m) {
    try {
      const out = await runRestartScript(m);
      if (!out.res) { notify({ title: "Claude restart failed", body: (out.err || "no result").slice(0, 200), level: "warning", timeout: 15000 }); return; }
      if (out.res.busy) { notify({ title: "Claude restart", body: "already running", timeout: 4000 }); return; }
      const ok = out.res.restarted ?? [], sk = out.res.skipped ?? [];
      notify({ title: `${machineLabel(m)}: ${ok.length} restarted${sk.length ? `, ${sk.length} skipped` : ""}`,
               body: [...ok, ...sk.map((x) => `– ${x}`)].join(" · ").slice(0, 300) || "nothing to restart", timeout: 15000 });
    } catch (e) {
      notify({ title: "Claude restart failed", body: String(e?.message ?? e), level: "warning", timeout: 15000 });
    } finally { this.restarting[m] = false; await this.refreshVersions(cx); }
  }

  // One reboot (bed) button per computer. The count of outdated sessions sits on the bed icon
  // like an inventory stack count. Clickable only with something to restart (or to confirm).
  restartChip(t, m) {
    const n = this.outdated(m);
    if (!this.versions[m]) return null;
    const busy = Boolean(this.restarting[m]);
    const armed = this.armed === m;
    const text = busy ? `${machineLabel(m)} 리부트 중…` : armed ? `${machineLabel(m)} ${n}개 리부트? 한 번 더` : `${machineLabel(m)} 리부트`;
    const idle = !busy && !armed && n === 0;
    const icon = div().relative().w(18).h(18).flex_none()
      .child(image("mods/mc-status/art/bed.svg").size(18).absolute().left(0).top(0).when(busy, (el) => el.opacity(Math.floor(Date.now() / 400) % 2 ? 1 : 0.35)))
      .when(n > 0 && !busy, (el) => el.child(div().absolute().right(-3).bottom(-4).child(outlined(String(n), "#ffffff", 11, false))));
    return div().id(`restart-${m || "local"}`).flex_none().border(1).border_color(armed ? "#ffffff" : "#000000").cursor_pointer()
      .tooltip(`${machineLabel(m)}: 옛 버전 세션 ${n}개 (작업 중인 세션은 건너뜀) · 두 번 눌러 실행`)
      .on_click((_e, cx) => { if (n > 0 || armed) this.clickRestart(cx, m); })
      .child(div().border_b(2).border_color("#3a3a3a")
        .child(h_flex().px(6).h(22).gap(6).items_center().border_t(2).border_color(idle || busy ? "#8a8a8a" : "#b5b5b5")
          .bg(armed ? "#8a3a3a" : idle || busy ? "#5d5d5d" : "#7c7c7c").when(!idle && !busy, (el) => el.hover((s) => s.bg(armed ? "#a04848" : "#8f9fd0")))
          .text_color(idle || busy ? "#c8c8c8" : "#ffffff")
          .child(icon).child(text)));
  }

  // The house menu (a Minecraft-style pause menu): restore, and a reboot button per computer.
  houseMenu() {
    return h_flex().id("house-menu").absolute().left(64).bottom(GROUND_H + 8).gap(4).p(5)
      .bg("#000000b8").border(1).border_color("#000000")
      .on_mouse_down("left", (_e, cx) => cx.stop_propagation())
      .child(this.button("house-respawn", this.busy ? this.label : "복구", (_e, cx) => {
        this.menuOpen = false; cx.notify();
        cx.spawn(async (cx) => { await this.runRestore(cx, true); });
      }, this.busy, `${ICONS}/totem.svg`, "불사의 토템: 닫힌 Claude 세션을 다시 엽니다"))
      .children(this.machines().map((m) => this.restartChip(null, m)).filter(Boolean));
  }


  async runRestore(cx, manual) {
    if (this.busy) return;
    this.busy = true; this.label = "복구 중…"; cx.notify();
    try { report(await runScript("both"), manual); }
    catch (e) { notify({ title: "Claude restore failed", body: String(e?.message ?? e), level: "warning", timeout: 15000 }); }
    finally { this.busy = false; this.label = "↻ 복구"; cx.notify(); }
  }

  // The palette key as actually bound, not a hardcoded one.
  hint() {
    const mac = window()?.platform === "macos";
    const mod = { cmd: mac ? "⌘" : "Ctrl+", ctrl: mac ? "⌃" : "Ctrl+", shift: mac ? "⇧" : "Shift+", alt: mac ? "⌥" : "Alt+", option: mac ? "⌥" : "Alt+" };
    const b = keys().find((k) => k.section === "global" && k.action === "app.palette");
    const parts = b && b.keys.endsWith("--") ? [...b.keys.slice(0, -2).split("-"), "-"] : b?.keys.split("-");
    const key = parts && parts.map((p) => mod[p.toLowerCase()] ?? p.toUpperCase()).join("");
    return key ? `${key}  commands` : "commands";
  }

  // ── look ──────────────────────────────────────────────────────────
  // The yard: grass, dirt, trees, flowers and a pond along the bottom; the sky above it is the
  // layout's own background (day or night). Cats keep a fixed spot each (sorted by session),
  // so a status change never reshuffles them. They're frame strips (this app shows only a GIF's
  // first frame) stepped by one 200 ms clock that runs only while the window is visible.

  cats() {
    const list = agents();
    const seen = new Set(list.map((a) => a.address));
    const byAddr = new Map(terminals().map((t) => [t.address, t]));
    const cats = list.map((a) => {
      const l = byAddr.get(a.address)?.labels ?? {};
      return { key: a.address, pane: a.pane, status: a.status, name: a.tab_name || a.space_name || a.address,
               model: l["cc.model"] ?? null, ctx: l["cc.ctx"] ?? null };
    });
    // A Claude session whose program exited but whose terminal is still in a tab: a sleeping cat.
    for (const t of byAddr.values()) {
      const l = t.labels ?? {};
      if (seen.has(t.address) || t.state !== "live" || !l["cc.model"] || !l["herdr.tab"]) continue;
      cats.push({ key: t.address, pane: null, terminal: t.address, status: "off", name: t.name || t.address, model: l["cc.model"], ctx: null });
    }
    return cats;
  }

  // Which strip and frame a cat shows now. A checked (idle) cat sits for a while, lies down once, then rests.
  pose(c, now) {
    const h = hashOf(c.key);
    const since = this.since.get(c.key)?.at ?? now;
    let anim = { working: "walk", blocked: "gift", done: "done", off: "sleep" }[c.status] ?? "idle";
    let f = null;
    if (c.status === "idle") {
      const sitFor = 25000 + (h % 20000), e = now - since;
      if (e >= sitFor + 6 * 300) anim = "rest";
      else if (e >= sitFor) { anim = "liedown"; f = Math.min(5, Math.floor((e - sitFor) / 300)); }
    }
    const m = META[anim];
    if (f == null) f = Math.floor((this.vclock ?? 0) / PERIOD[anim] + (h % 97)) % (anim === "walk" ? m.seq.length : m.n);
    return { anim, m, f };
  }

  cat(c, x, lane, now) {
    const coat = coatOf(c.key);
    const tip = [c.name, { working: "running around", idle: "checked — taking it easy", off: "asleep (session closed)", blocked: "brought you a gift — needs you", done: "done — XP collected" }[c.status] ?? c.status,
      c.model, c.ctx ? `ctx ${c.ctx}%` : null].filter(Boolean).join(" · ");
    const { anim, m, f } = this.pose(c, now);
    // Each cat keeps its own slight turn (±10°): lying strips have 10 variants (5 turns × mirrored),
    // sitting ones 5 (the turns); the same turn index is used for both, so lying down starts where it sat.
    const lv = (hashOf(c.key) >>> 5) % 10;
    const vi = m.variants >= 10 ? lv : lv >> 1;
    const strip = m.variants ? `${CATS}/${coat}-${anim}-${vi}.png` : `${CATS}/${coat}-${anim}.png`;
    // a lying cat rests its body on the grass; the tail may hang into it (rows baked per variant, +3 so the belly settles into the grass)
    const sink = m.sink ? m.sink[vi] + 3 : m.sinkF ? m.sinkF[vi][f] + 3 : 0;
    if (anim === "walk") {
      const [dx, fi] = m.seq[f];
      return div().absolute().left(x - m.span / 2).bottom(GROUND_H + lane).w(m.span).h(m.h)
        .child(frame(strip, m, fi).absolute().left(dx).top(0)
          .id(`cat-${c.key}`).cursor_pointer().tooltip(tip)
          .on_click(() => run("pane.focus", { pane: c.pane })));
    }
    return frame(strip, m, f).when(c.status === "off", (el) => el.opacity(0.85))
      .id(`cat-${c.key}`).absolute().left(x - m.w / 2).bottom(GROUND_H + lane - sink).cursor_pointer()
      .tooltip(tip)
      .on_click(() => (c.pane ? run("pane.focus", { pane: c.pane }) : run("pane.focus", { terminal: c.terminal })));
  }

  // Day or night: swaps the sky picture behind the tab bar, terminals and yard.
  // Rewrites this layout's own file (the app applies a layout edit at once and keeps it).
  async toggleSky() {
    const file = `${appHome()}/layouts/${shared("layout") || "minecraft"}.json`;
    const text = await readTextFile(file).catch(() => null);
    if (!text) return;
    const doc = JSON.parse(text);
    const night = String(doc.background?.image ?? "").includes("night");
    doc.background = { image: `${SCENE}/sky2-${night ? "day" : "night"}.png`, fit: "cover" };
    await writeTextFile(file, JSON.stringify(doc, null, 2), text).catch((e) => notify({ title: "Sky", body: String(e?.message ?? e), level: "warning" }));
  }

  // A Minecraft-style stone button: dark outline, light top edge, dark bottom edge.
  button(id, text, onClick, disabled, icon, tip) {
    return div().id(id).flex_none().border(1).border_color("#000000").cursor_pointer()
      .on_click(onClick).when(Boolean(tip), (el) => el.tooltip(tip))
      .child(div().border_b(2).border_color("#3a3a3a")
        .child(h_flex().px(6).h(20).gap(5).items_center().border_t(2).border_color(disabled ? "#8a8a8a" : "#b5b5b5")
          .bg(disabled ? "#5d5d5d" : "#7c7c7c").hover((s) => s.bg("#8f9fd0"))
          .text_color(disabled ? "#c8c8c8" : "#ffffff")
          .when(Boolean(icon), (el) => el.child(image(icon).size(16).when(Boolean(disabled), (el) => el.opacity(0.55))))
          .child(text.replace("↻ ", ""))));
  }

  // A limit as a survival row, like the game's HUD: ten pips (half pips at 5%) of what's left.
  // 7d is health (hearts, filling from the left), 5h is hunger (shanks, filling from the right).
  limitRow(key, periodSec, pip) {
    const l = this.data?.lim?.[key] ?? readLimit(key);
    if (!l) return null;
    const left = Math.max(0, 100 - l.used);
    const { zone, sev } = paceZone(l.used, l.resets, periodSec);
    if (zone !== "ok") { this.hudLive = true; this.fast = true; }
    const tick = Math.floor((this.vclock ?? 0) / 100);
    const jitter = (i) => { const h = ((i + 1) * 2654435761 + tick * 40503) >>> 0; return (h % 3) - 1; };
    const now = Date.now();
    const H = pip === "heart" ? 16 : 18;
    let pips = Array.from({ length: 10 }, (_, i) => {
      const v = left - i * 10;
      return { kind: v >= 10 ? "" : v >= 5 ? "-half" : "-empty" };
    });
    if (pip === "shank") pips = pips.reverse();          // hunger fills from the right, as in the game
    // The bar redraws every 100 ms while this runs; a wave step is exactly one redraw.
    const wave = Math.floor((this.vclock ?? 0) / 100) % 14;   // one pip per tick: all 10 hop in turn, then a rest
    const els = pips.map(({ kind }, k) => {
      const filled = kind !== "-empty";
      const hop = zone === "good" && k === wave;
      const trail = zone === "good" && k === wave - 1;
      // strength scales with how comfortable (good) or how far behind (bad) the pace is
      const g = zone === "good" ? sev : 0;
      const amp = 1 + Math.round(2 * sev);
      const dy = hop ? -Math.round(2 + 3 * g) : zone === "bad" ? jitter(k) * amp : 0;
      // regeneration: the hopping pip flashes white-edged and glows; poison: tinted by how far into the red
      return div().relative().w(18).h(H).flex_none().mr(-2).top(dy)
        .when(filled && (hop || trail), (el) => el.child(image(`${ICONS}/${pip}-hl.svg`).w(26).h(H + 8).absolute().left(-4).top(-4).opacity(hop ? 0.2 + 0.45 * g : 0.08 + 0.2 * g)))
        .child(image(`${ICONS}/${pip}${hop && filled && kind === "" && g >= 0.3 ? "-hl" : kind}.svg`).w(18).h(H).absolute().left(0).top(0))
        .when(zone === "bad" && filled, (el) => el.child(image(`${ICONS}/${pip}${kind}-poison.svg`).w(18).h(H).absolute().left(0).top(0).opacity(sev)));
    });
    return { l, left, zone, col: limitColor(l.used, l.resets, periodSec), pips: els };
  }

  // Everything render() needs from Herdr, read once per data change.
  readData() {
    const fa = focused()?.agent ?? null;
    const ft = fa ? terminals().find((t) => t.address === fa) : null;
    return {
      space: spaces().find((s) => s.active),
      cats: this.cats(),
      night: String(layout()?.background?.image ?? "").includes("night"),
      lim: { "cc.seven": readLimit("cc.seven"), "cc.five": readLimit("cc.five") },
      focusedAgent: fa,
      focusedLabels: ft?.labels ?? {},
      hint: this.hint(),
    };
  }

  render() {
    // (a data change that lands on the same redraw as a tick is picked up within 2 s at most)
    const fresh = !this.animOnly || !this.data || Date.now() - this.dataAt > 2000;
    this.animOnly = false;
    if (fresh) { this.data = this.readData(); this.dataAt = Date.now(); }
    const D = this.data;
    const space = D.space;
    const cats = D.cats;
    this.catsOut = cats.length > 0;
    this.fast = cats.some((c) => c.status === "working");
    const now = Date.now();
    for (const c of cats) {                                  // when each cat's status last changed
      const prev = this.since.get(c.key);
      if (!prev || prev.status !== c.status) this.since.set(c.key, { status: c.status, at: now });
    }
    const needs = cats.filter((c) => c.status === "blocked").length;
    const running = cats.filter((c) => c.status === "working").length;
    const night = D.night;
    const ink = night ? "#d6dcf5" : "#ffffff";

    const W = this.yardW ?? 1600;
    const RIGHT_W = 200, HOUSE_W = 70, HUD_W = 372;
    const hud0 = W / 2 - HUD_W / 2 - 40, hud1 = W / 2 + HUD_W / 2 + 40;
    // fixed spots, sorted by session, spread over the yard left and right of the HUD
    const lo = HOUSE_W + 90, hi = Math.max(lo + 60, W - RIGHT_W - 90);
    const spans = [[lo, Math.max(lo, Math.min(hud0, hi))], [Math.min(hud1, hi), hi]].filter(([a, b]) => b - a > 40);
    const total = spans.reduce((n, [a, b]) => n + b - a, 0) || 1;
    const spotAt = (f) => { let d = f * total; for (const [a, b] of spans) { if (d <= b - a) return a + d; d -= b - a; } return hi; };
    const order = [...cats].sort((a, b) => String(a.key).localeCompare(String(b.key)));
    // room per cat: the small per-cat offset shrinks when they stand close
    const gap = total / Math.max(1, order.length);
    const wob = Math.min(10, Math.floor(gap * 0.08));
    const placed = order.map((c, i) => {
      const h = hashOf(c.key);
      return { c, x: spotAt((i + 0.5) / order.length) + (wob ? (h % (2 * wob + 1)) - wob : 0) };
    });

    return div().id("mc-status").relative().size_full().overflow_hidden().text_size(11)
      .on_size_change((size, cx) => { const w = Math.round(size.width / (settings()?.zoom || 1)); if (w !== this.yardW) { this.yardW = w; cx.notify(); } })
      .child(skyLife(W, night))
      .child(scenery(W, RIGHT_W))
      .child(ground())
      .child(div().id("house").absolute().left(10).bottom(GROUND_H).cursor_pointer()
        .tooltip("집: 복구 · 리부트")
        .on_click((_e, cx) => { this.menuOpen = !this.menuOpen; this.armed = null; cx.notify(); })
        .child(image("mods/mc-status/art/house.svg").w(48).h(48))
        .when(this.busy || Object.values(this.restarting ?? {}).some(Boolean), (el) => el.child(image(this.busy ? `${ICONS}/totem.svg` : "mods/mc-status/art/bed.svg").size(16)
          .absolute().left(16).top(-14).opacity(Math.floor(Date.now() / 400) % 2 ? 1 : 0.35))))
      .when(cats.length === 0, (el) => el.child(div().absolute().left(HOUSE_W + 20).bottom(GROUND_H + 10).child(shadow("no cats yet — start a Claude session", ink))))
      .children([...placed].sort((a, b) => (a.c.status === "working") - (b.c.status === "working")).map(({ c, x }) => this.cat(c, x, 0, now)))
      .child(this.hud(W, HUD_W, ink))
      .child(v_flex().absolute().right(10).top(6).gap(4).items_end()
        .child(h_flex().gap(8).items_center()
          .child(h_flex().gap(4).items_center().child(image(`${ICONS}/${space?.machine ? "ender-pearl" : "grass-block"}.svg`).size(14)).child(shadow(space?.machine ?? "This computer", ink)))
          .when(Boolean(space?.branch), (el) => el.child(h_flex().gap(4).items_center().child(image(`${ICONS}/rail.svg`).size(14)).child(shadow(space.branch, ink)))))
        .child(h_flex().gap(6).items_center()
          .child(shadow(`${cats.length} cats · ${running} running`, ink))
          .when(needs > 0, (el) => el.child(shadow(`${needs} need${needs === 1 ? "s" : ""} you`, "#ff6b6b"))))
        .child(h_flex().gap(6)
          .child(this.button("sky-btn", night ? "Night" : "Day", (_e, cx) => { cx.spawn(async () => { await this.toggleSky(); }); }, false,
            `${ICONS}/${night ? "moon" : "sun"}.svg`, "Switch the sky: day / night"))
          // The command palette is a command block.
          .child(this.button("palette", "", () => run("app.palette"), false, `${ICONS}/command-block.svg`, D.hint))))
      .when(this.menuOpen, (el) => el.child(this.houseMenu()));
  }

  // The HUD, centred like the game's: health (7d) left, hunger (5h) right, the XP bar under them.
  // XP = how full the focused session's context is; the number is that %.
  hud(W, HUD_W, ink) {
    this.hudLive = false;
    const health = this.limitRow("cc.seven", 7 * 86400, "heart");
    const hunger = this.limitRow("cc.five", 5 * 3600, "shank");
    const fa = this.data.focusedAgent;
    const ft = { labels: this.data.focusedLabels };
    const ctx = Number.parseFloat(ft?.labels?.["cc.ctx"]);
    const xp = Number.isFinite(ctx) ? Math.max(0, Math.min(100, Math.round(ctx))) : null;
    const BAR = HUD_W - 8;
    // The held-item name, as in the game: the focused session's model, in its statusline colour.
    // It shows bright when you switch sessions, then settles to a dimmer glow.
    const model = ft?.labels?.["cc.model"] || null;
    if (fa !== this.heldFor) { this.heldFor = fa; this.heldAt = Date.now(); }
    const fresh = Date.now() - (this.heldAt ?? 0) < 4000;
    const caption = (r, label) => r
      ? h_flex().gap(5).child(outlined(label, "#ffffff", 11, false)).child(outlined(`${r.l.used}%`, r.col, 11, false)).child(outlined(fmtLeft(r.l.resets), "#ffffff", 11, false))
      : outlined(`${label} —`, "#ffffff", 11, false);
    return v_flex().absolute().left(Math.round(W / 2 - HUD_W / 2)).bottom(3).w(HUD_W).gap(1)
      .child(h_flex().id("hud-model").h(19).justify_center().tooltip(model ? `Model of the focused session: ${model}` : "No session focused")
        .when(Boolean(model), (el) => el.child(div().opacity(fresh ? 1 : 0.85).transition("opacity", { duration: 600 })
          .child(glowText(model, modelColor(model), 15)))))
      // The 7d / 5h captions show only while the pointer is over their bar (coloured, as before).
      .child(h_flex().h(14).justify_between().px(4).text_size(10.5)
        .child(div().when(this.hoverLim === "7d", (el) => el.child(caption(health, "7d"))))
        .child(div().when(this.hoverLim === "5h", (el) => el.child(caption(hunger, "5h")))))
      .child(div().relative().w_full().h(18)
        .child(h_flex().id("hud-7d").absolute().left(4).top(0).min_h(18).min_w(160)
          .on_hover((on, cx) => { this.hoverLim = on ? "7d" : this.hoverLim === "7d" ? null : this.hoverLim; cx.notify(); })
          .children(health?.pips ?? []))
        .child(h_flex().id("hud-5h").absolute().right(6).top(0).min_h(18).min_w(160)
          .on_hover((on, cx) => { this.hoverLim = on ? "5h" : this.hoverLim === "5h" ? null : this.hoverLim; cx.notify(); })
          .children(hunger?.pips ?? [])))
      .child(div().id("hud-xp").relative().h(22).tooltip(xp == null ? "XP: context of the focused session (no data yet)" : `XP: the focused session has used ${xp}% of its context`)
        .child(div().absolute().left(4).bottom(0).w(364).h(10)
          .child(image(`${ICONS}/xpbar-bg.png`).w(364).h(10).absolute().left(0).top(0))
          .child(div().absolute().left(0).top(0).h(10).w(Math.round(364 * (xp ?? 0) / 100)).overflow_hidden()
            .child(image(`${ICONS}/xpbar-fill.png`).w(364).h(10).absolute().left(0).top(0))))
        .when(xp != null, (el) => el.child(h_flex().absolute().left(0).w_full().top(0).justify_center().child(outlined(String(xp), "#80ff20", 13)))));
  }
}

// The same family colours as ~/.claude/statusline.js
const MODEL_COLOR = { opus: "#cba6f7", sonnet: "#fab387", haiku: "#94e2d5", fable: "#f5c2e7" };
function modelColor(m) {
  const fam = (String(m).toLowerCase().match(/opus|sonnet|haiku|fable/) || [])[0];
  return MODEL_COLOR[fam] ?? "#ffffff";
}

// The held-item name made to glow: a brighter colour, a steady soft halo of the same colour,
// the black outline, and a few twinkling sparkles at the corners.
function lighten(hex, k) {
  const n = hex.replace("#", "");
  const c = [0, 2, 4].map((i) => parseInt(n.slice(i, i + 2), 16));
  return "#" + c.map((v) => Math.round(v + (255 - v) * k).toString(16).padStart(2, "0")).join("");
}
// The statusline colour pushed to full saturation (same hue), so the name reads as a coloured item
// name rather than near-white.
function vivid(hex, sat = 1, light = 0.62) {
  const n = hex.replace("#", "");
  const [r, g, b] = [0, 2, 4].map((i) => parseInt(n.slice(i, i + 2), 16) / 255);
  const mx = Math.max(r, g, b), mn = Math.min(r, g, b), d = mx - mn;
  let h = 0;
  if (d) h = mx === r ? ((g - b) / d) % 6 : mx === g ? (b - r) / d + 2 : (r - g) / d + 4;
  h = (h * 60 + 360) % 360;
  const c = (1 - Math.abs(2 * light - 1)) * sat, x = c * (1 - Math.abs(((h / 60) % 2) - 1)), m = light - c / 2;
  const [R, G, B] = h < 60 ? [c, x, 0] : h < 120 ? [x, c, 0] : h < 180 ? [0, c, x] : h < 240 ? [0, x, c] : h < 300 ? [x, 0, c] : [c, 0, x];
  return "#" + [R, G, B].map((v) => Math.round((v + m) * 255).toString(16).padStart(2, "0")).join("");
}
function glowText(text, color, size) {
  const bright = vivid(color, 0.7, 0.7);
  color = vivid(color, 0.7, 0.6);
  const copy = (dx, dy, c) => div().absolute().left(dx).top(dy).whitespace_nowrap().text_color(c).child(text);
  const HALO = [[-2, 0], [2, 0], [0, -2], [0, 2], [-2, -2], [2, -2], [-2, 2], [2, 2], [-3, 0], [3, 0]];
  const spark = (left, top, delay) => div().absolute().left(left).top(top).size(2).bg("#ffffff")
    .opacity((Math.floor((Date.now() + delay) / 600) % 3) === 0 ? 1 : 0.15);
  return h_flex().relative().flex_none().text_size(size).font_bold()
    .child(div().whitespace_nowrap().text_color(bright).child(text))
    .child(div().absolute().left(0).top(0).size_full().opacity(0.25)
      .children(HALO.map(([dx, dy]) => copy(dx, dy, color))))
    .child(copy(-1, 0, "#000000")).child(copy(1, 0, "#000000")).child(copy(0, -1, "#000000")).child(copy(0, 1, "#000000"))
    .child(copy(0, 0, bright))
    .child(spark(-5, -2, 0)).child(spark(-3, size - 2, 500)).child(div().absolute().right(-5).top(1).size(2).bg("#ffffff")
      .opacity((Math.floor((Date.now() + 300) / 700) % 3) === 0 ? 1 : 0.15));
}

// Text with the game's drop shadow.
function shadow(text, color) {
  return h_flex().relative().flex_none()
    .child(div().flex_none().whitespace_nowrap().text_color(color).child(text))
    .child(div().absolute().left(1).top(1).whitespace_nowrap().text_color("#000000b0").child(text))
    .child(div().absolute().left(0).top(0).whitespace_nowrap().text_color(color).child(text));
}

// The XP number: bright green with a black outline.
function outlined(text, color, size, bold = true) {
  const o = (dx, dy, c = "#000000") => div().absolute().left(dx).top(dy).whitespace_nowrap().text_color(c).child(text);
  return h_flex().relative().flex_none().text_size(size).when(bold, (el) => el.font_bold())
    .child(div().whitespace_nowrap().text_color(color).child(text))
    .child(o(-1, 0)).child(o(1, 0)).child(o(0, -1)).child(o(0, 1)).child(o(0, 0, color));
}

// One frame of a sprite strip: a window the size of a frame over the whole strip.
function frame(strip, m, i) {
  return div().w(m.w).h(m.h).flex_none().overflow_hidden().relative()
    .child(image(strip).w(m.w * m.n).h(m.h).absolute().top(0).left(-m.w * i));
}

// ── scenery ───────────────────────────────────────────────────────────
const GROUND_H = 16;
const SCENE = "mods/mc-status/art/scene";
// frame times are whole ticks (100 ms) so no frame is shown shorter than the others
const PERIOD = { walk: 100, idle: 100, rest: 200, sleep: 200, gift: 100, done: 100, liedown: 300 };
const hashOf = (k) => [...String(k)].reduce((h, ch) => (h * 33 + ch.charCodeAt(0)) >>> 0, 5381);
function findNode(n, id) {
  if (!n) return null;
  if (n.id === id) return n;
  for (const c of n.children ?? []) { const r = findNode(c, id); if (r) return r; }
  return null;
}
const PROP = { oak: [56, 56], birch: [44, 60], poppy: [9, 18], dandelion: [9, 15], cornflower: [9, 15], allium: [12, 18], tuft: [15, 12],
  cane: [12, 40], lily: [15, 9], tulip: [9, 18], oxeye: [9, 18], cloud: [108, 30] };
const prop = (name, x, dy = 0) => image(`${SCENE}/${name}.png`).w(PROP[name][0]).h(PROP[name][1]).absolute().left(x).bottom(GROUND_H + dy);

// Behind the cats: the house, one tree at each end (cats never sit in front of leaves, so the XP orb
// stays visible), and mostly flowers.
function scenery(W, signW) {
  const span = W - signW;
  return div().absolute().left(0).top(0).size_full()
    .child(prop("oak", 66))
    // on a narrow window the birch would stand in the HUD: then leave it out
    .when(span - 70 > W / 2 + 372 / 2 + 40, (el) => el.child(prop("birch", span - 70)))
    .child(prop("cane", POND_X - 14)).child(prop("cane", POND_X + 88));
}

// The sky over the yard keeps moving: clouds drift by day, stars twinkle at night.
// (The big sky behind the terminals is the layout's picture and can't move.)
function skyLife(W, night) {
  if (night) {
    const STARS = Array.from({ length: 14 }, (_, i) => [(i * 137 + 40) % Math.max(200, W - 320), 6 + (i * 23) % 34]);
    return div().absolute().left(0).top(0).size_full()
      .children(STARS.map(([x, y], i) => div().absolute().left(x).top(y).size(i % 4 ? 2 : 3).bg("#f4f1d0")
        .opacity(0.35 + 0.65 * (0.5 + 0.5 * Math.sin(Date.now() / (300 + i * 60) + i)))));
  }
  const cloud = (top, from, to, period, scale) => image(`${SCENE}/cloud.png`).w(108 * scale).h(30 * scale).absolute().top(top)
    .left(Math.round(from + (to - from) * ((Date.now() % period) / period)));
  return div().absolute().left(0).top(0).size_full()
    .child(cloud(2, -120, W - 200, 140000, 1))
    .child(cloud(14, W * 0.6, -160, 190000, 0.7));
}

// The ground strip: grass, dirt, flowers, pond and lily baked into one picture (gen_scene.py);
// only the water's two shimmer lines are live (native loops).
const POND_X = 1180;
function ground() {
  return div().absolute().left(0).bottom(0).w(3200).h(40)
    .child(image(`${SCENE}/yard-ground.png`).w(3200).h(40).absolute().left(0).top(0))
    .child(div().absolute().left(POND_X + 12).top(29).w(9).h(2).bg("#9cc0ff").opacity(0.3 + 0.7 * (0.5 + 0.5 * Math.sin(Date.now() / 350))))
    .child(div().absolute().left(POND_X + 48).top(32).w(12).h(2).bg("#9cc0ff").opacity(0.3 + 0.7 * (0.5 + 0.5 * Math.cos(Date.now() / 420))));
}
