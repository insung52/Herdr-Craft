import { View, div, svg, image } from "gpui-kit";
import { h_flex, ScrollHandle } from "gpui-base";
import { spaces, panes, run, openOverlay, theme, window, shared, layout, settings } from "herdr";

// Minecraft stone button look: black outline (white when selected), light top edge, dark bottom edge,
// grey face that turns blue-grey under the pointer. `el` must not set its own bg/border.
const STONE = { face: "#6f6f6f", hover: "#7d85b8", hi: "#a9a9a9", lo: "#3f3f3f", text: "#ffffff", sub: "#dcdcdc" };
function stone(el, on = false) {
  return el.relative().border(1).border_color(on ? "#ffffff" : "#000000").bg(on ? "#7a7a7a" : STONE.face)
    .hover((s) => s.bg(STONE.hover))
    .child(div().absolute().left(0).right(0).top(0).h(2).bg(STONE.hi))
    .child(div().absolute().left(0).right(0).bottom(0).h(2).bg(STONE.lo));
}

// A Minecraft stone button with a "+" (new space, new tab).
const mcPlus = (id, tip, onClick, size = 18) => div().id(id).flex_none().border(1).border_color("#000000").cursor_pointer()
  .tooltip(tip).on_mouse_down("left", (_e, cx) => cx.stop_propagation())
  .on_click((e, cx) => { cx.stop_propagation(); onClick(e, cx); })
  .child(div().border_b(2).border_color("#3a3a3a")
    .child(div().w(size).h(size - 4).flex().items_center().justify_center().border_t(2).border_color("#b5b5b5")
      .bg("#7c7c7c").hover((s) => s.bg("#8f9fd0")).text_color("#ffffff").text_size(13).child("+")));

function find(node, id) {
  if (node?.id === id) return node;
  for (const child of node?.children ?? []) {
    const found = find(child, id);
    if (found) return found;
  }
  return null;
}

// Same as the agents mod: drops a status glyph, keeps a leading bracket or quote.
const clean = (s) => (s ?? "").replace(/^[^\p{L}\p{N}\p{Ps}\p{Pi}]+/u, "").replace(/^\[ [!.] \] /, "").trim();

// Each agent keeps one cat coat everywhere (list, tabs, pane header, yard): picked from its address.
const COATS = ["ginger", "tuxedo", "black", "calico", "siamese", "gray", "white"];
const coatOf = (addr) => { let h = 0; for (const ch of String(addr ?? "")) h = (h * 31 + ch.charCodeAt(0)) >>> 0; return COATS[h % COATS.length]; };
const CATS = "mods/mc-status/art/cats8";

// A tab Herdr named (unnamed, or after its program) follows its agent's live
// title, as the agents list does; a name the person gave stays.
function label(tab, lead) {
  const prog = lead?.program?.name;
  const base = tab.named ? tab.name : prog ?? "Terminal";
  if (!lead?.program?.agent) return base;
  const live = clean(lead.title);
  // clean() would strip a path's leading ~ or /: test the title with only its status glyph gone.
  const path = /^[~/]|^[A-Za-z]:\\/.test((lead.title ?? "").replace(/^[^\p{L}\p{N}~/]+/u, ""));
  const telling = live && live !== lead.terminal && live !== prog && !path && !live.includes("@") && live.toLowerCase() !== lead.program.key;
  return (tab.name === prog || !tab.named) && telling ? live : base;
}

export default class Tabs extends View {
  init() {
    this.pressed = null;
    this.scroll = ScrollHandle.new();
    try { this.panels = JSON.parse(localStorage.getItem("panels") ?? "{}"); } catch { this.panels = {}; }
    if (!this.panels || typeof this.panels !== "object" || Array.isArray(this.panels)) this.panels = {};
    this.swipe = { acc: 0, steps: 0, at: 0, last: 0 };
  }

  // One tab per wheel notch. A touchpad or smooth-scrolling mouse sends many
  // small events per gesture: a short swipe or one smoothed notch (about
  // 25 px) switches one tab, a longer swipe keeps going a tab per 60 px, at
  // most one every 100 ms so each shows.
  wheel(e) {
    if (e.delta_lines) {
      if (e.delta_lines.y) run(e.delta_lines.y > 0 ? "tab.prev" : "tab.next");
      return;
    }
    const s = this.swipe, now = Date.now();
    // Phases often arrive only as moves (a macOS touchpad included): a pause
    // or a turn starts a new gesture.
    if (e.touch_phase === "started" || now - s.at > 250 || e.delta.y * s.acc < 0) Object.assign(s, { acc: 0, steps: 0 });
    s.at = now;
    s.acc += e.delta.y;
    const need = s.steps ? 60 : 20;
    if (Math.abs(s.acc) < need || now - s.last < 100) return;
    s.acc -= Math.sign(s.acc) * need;
    s.steps++;
    s.last = now;
    run(e.delta.y > 0 ? "tab.prev" : "tab.next");
  }

  // The side panel is remembered per space: switching shows that space's choice
  // (closed if it never had one), and opening or closing it records it.
  syncPanel(space, panel, body, enabled) {
    if (!space || !panel) return;
    const now = panel.hidden ? null : body?.active ?? null;
    if (space.id !== this.space) {
      const first = this.space === undefined;
      this.space = space.id; this.pending = null;
      if (!(first && !(space.id in this.panels))) {
        const stored = this.panels[space.id] ?? null, want = enabled.includes(stored) ? stored : null;
        if (want !== now) {
          this.pending = { want, until: Date.now() + 1000 };
          if (want) { run("layout.select", { stack: "panel-body", child: want }); run("layout.show", { id: "panel" }); }
          else run("layout.hide", { id: "panel" });
          return;
        }
      }
    }
    // Until the restore lands (or something else won), the old state isn't a choice.
    if (this.pending) {
      if (this.pending.want !== now && Date.now() < this.pending.until) return;
      this.pending = null;
    }
    if (this.panels[space.id] === now) return;
    this.panels[space.id] = now;
    localStorage.setItem("panels", JSON.stringify(this.panels));
  }

  render() {
    const t = theme();
    const space = spaces().find(p => p.active);
    const shown = space?.tabs ?? [];
    const active = shown.findIndex(tab => tab.active);
    const selected = shown[active]?.id;
    if (selected !== this.selected || active !== this.selectedIndex) {
      this.selected = selected;
      this.selectedIndex = active;
      if (active >= 0) this.scroll.scroll_to_item(active);
    }
    const stop = (_e, cx) => cx.stop_propagation();
    const button = (id, label, action) => stone(div().id(id).size(24).ml(2).flex_none().flex().items_center().justify_center().text_color(STONE.text))
      .on_mouse_down("left", stop).on_click(action).child(label);
    const item = (c, i) => {
      const lead = panes().find(p => p.tab === c.id && p.program?.agent) ?? panes().find(p => p.tab === c.id);
      const program = lead?.program;
      const name = label(c, lead);
      return h_flex().id(`tab-${c.id}`).h(29).px(10).gap(7).items_center().flex_none().text_size(12.8)
        // A rename or status dot on this or an earlier tab can push the active one out.
        .when(i <= active, el => el.on_size_change((_size, cx) => { this.scroll.scroll_to_item(active); cx.notify(); }))
        .map(el => stone(el, c.active)).text_color(STONE.text)
        .on_mouse_down("left", (e, cx) => { cx.stop_propagation(); this.pressed = i; if (e.click_count === 2) run("tab.rename", { id: c.id }); })
        .on_mouse_up("left", () => {
          const from = this.pressed; this.pressed = null;
          if (from !== null && from !== i) run("tab.move", { id: shown[from].id, index: space.tabs.findIndex(x => x.id === c.id) + 1 });
          else run("tab.select", { id: c.id });
        })
        .on_mouse_down("right", (_e, cx) => { cx.stop_propagation(); openOverlay({ mod: "menu", kind: "popup", width: 200, props: { tab: "tab", target: { id: c.id, space: space.id } } }); })
        .when(Boolean(program?.agent && lead?.terminal), el => el.child(image(`${CATS}/${coatOf(lead.terminal)}-face-sm.png`).w(17).h(17)))
        .when(Boolean(program?.icon) && !(program?.agent && lead?.terminal), el => el.child(program.tint ? svg(program.icon).size(14).text_color(t.muted) : image(program.icon).size(14)))
        .child(div().max_w(170).truncate().child(c.zoomed ? `${name} Z` : name))
        .when(c.status === "working", el => el.child(image("mods/mc-status/art/torch.svg").size(15).flex_none()))
        .when(c.status === "blocked", el => el.child(image("mods/mc-status/art/gift.svg").size(16).flex_none()))
        .when(c.status === "done", el => el.child(image("mods/mc-status/art/xp.svg").size(16).flex_none()))
        .when(c.active, el => el.child(div().id(`close-${c.id}`).text_color(t.dim).on_mouse_down("left", stop).on_click((_e, cx) => { cx.stop_propagation(); run("tab.close", { id: c.id }); }).child(svg("mods/pane/close.svg").size(12))));
    };
    const root = layout(), sidebar = find(root, "sidebar"), w = window();
    // Old saved rails and a dragged-narrow sidebar can be smaller than the window buttons.
    const lightsPadding = w?.platform === "macos" && w.titlebar === "none" && !w.fullscreen && root?.traffic_lights
      ? Math.max(10, (root.traffic_lights[0] + 64) / settings().zoom - (sidebar?.hidden ? 0 : sidebar?.size?.px ?? 0))
      : 10;
    const panel = find(root, "panel"), body = find(root, "panel-body");
    const enabled = shared("workspace.panels") ?? ["files", "changes"];
    this.syncPanel(space, panel, body, enabled);
    const panelButton = (id, label, icon) => {
      const on = panel && !panel.hidden && body?.active === id;
      return h_flex().id(`panel-${id}`).h(26).px(8).gap(5).flex_none().items_center()
        .text_size(12).map(el => stone(el, on)).text_color(STONE.text).on_mouse_down("left", stop)
        .on_click(() => {
          if (on) run("layout.hide", { id: "panel" });
          else { run("layout.select", { stack: "panel-body", child: id }); run("layout.show", { id: "panel" }); }
        }).child(icon.startsWith("mods/mc-status") ? image(icon).size(16) : svg(icon).size(14)).child(label);
    };
    return h_flex().size_full().min_w(0).px(10).pl(lightsPadding).gap(3).items_center()
      .on_mouse_up("left", () => { this.pressed = null; })
      .on_scroll_wheel(e => this.wheel(e))
      .child(h_flex().id("tab-scroll").flex_1().min_w(0).h_full().items_center().gap(3).overflow_x_scrollbar().track_scroll(this.scroll)
        .on_size_change((_size, cx) => { if (active >= 0) { this.scroll.scroll_to_item(active); cx.notify(); } })
        .children(shown.map(item)))
      .child(div().mx(4).child(mcPlus("tab-new", "New tab", () => openOverlay({ mod: "new-menu", kind: "popup", width: 250, height: 512 }), 20)))
      .when(enabled.includes("files"), el => el.child(panelButton("files", "Files", "mods/mc-status/art/icons/chest.svg")))
      .when(enabled.includes("changes"), el => el.child(panelButton("changes", "Changes", "mods/mc-status/art/icons/book-quill.svg")))
      .when(w?.buttons, el => el.child(button("minimize", w.platform === "windows" ? svg("mods/mc-tabs/win-min.svg").size(16) : "−", () => run("window.minimize")))
        .child(button("maximize", w.platform === "windows" ? svg(`mods/mc-tabs/${w.maximized ? "win-restore" : "win-max"}.svg`).size(16) : "□", () => run("window.maximize")))
        .child(button("close-window", w.platform === "windows" ? svg("mods/mc-tabs/win-close.svg").size(16) : svg("mods/pane/close.svg").size(13), () => run("window.close"))));
  }
}
