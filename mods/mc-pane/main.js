// A pane's header, for layouts that frame their panes:
//   { "tab": "active", "pane": { "header": { "content": { "mod": "mc-pane" } } } }
// Shows the program's icon (the app's program table), the agent's name or
// the terminal's title, the folder, and the agent's status; buttons split, zoom and close
// this pane. Props from the app: { pane, terminal }. Click: focus the pane.

import { View, div, svg, image } from "gpui-kit";
import { h_flex } from "gpui-base";
import { panes, props, run, theme, home, layout } from "herdr";

// Minecraft stone button look: black outline (white when selected), light top edge, dark bottom edge,
// grey face that turns blue-grey under the pointer. `el` must not set its own bg/border.
const STONE = { face: "#6f6f6f", hover: "#7d85b8", hi: "#a9a9a9", lo: "#3f3f3f", text: "#ffffff", sub: "#dcdcdc" };
function stone(el, on = false) {
  return el.relative().border(1).border_color(on ? "#ffffff" : "#000000").bg(on ? "#7a7a7a" : STONE.face)
    .hover((s) => s.bg(STONE.hover))
    .child(div().absolute().left(0).right(0).top(0).h(2).bg(STONE.hi))
    .child(div().absolute().left(0).right(0).bottom(0).h(2).bg(STONE.lo));
}

// Each agent keeps one cat coat everywhere (list, tabs, pane header, yard): picked from its address.
const COATS = ["ginger", "tuxedo", "black", "calico", "siamese", "gray", "white"];
const coatOf = (addr) => { let h = 0; for (const ch of String(addr ?? "")) h = (h * 31 + ch.charCodeAt(0)) >>> 0; return COATS[h % COATS.length]; };
const CATS = "mods/mc-status/art/cats8";
// zoom looks through a spyglass; close is a barrier block
const MC = { zoom: "spyglass", unzoom: "spyglass", close: "barrier" };

// Match the first visible tab frame, including the active child of a stack.
function paneFrame(node) {
  if (!node || node.hidden) return null;
  if (node.content?.tab && node.content.pane) return node.content.pane;
  let children = node.children ?? [];
  if (node.type === "stack") {
    const visible = children.filter(child => !child.hidden);
    children = [visible.find(child => child.id === node.active) ?? visible[0]];
  }
  for (const child of children) {
    const frame = paneFrame(child);
    if (frame) return frame;
  }
  return null;
}

function icon(p, size, color) {
  if (!p?.icon) return null;
  return p.tint ? svg(p.icon).size(size).flex_none().text_color(color) : image(p.icon).w(size).h(size).flex_none();
}

function folder(cwd) {
  if (!cwd) return "";
  const h = home();
  return cwd === h ? "~" : cwd.startsWith(h + "/") ? "~" + cwd.slice(h.length) : cwd;
}

export default class Pane extends View {
  init() { this.hovered = false; }

  me() {
    return panes().find((p) => p.pane === props()?.pane);
  }

  button(t, id, icon, command, args) {
    return stone(div()
      .id(id)
      .p(2)
      .ml(2)
      .text_color(STONE.text))
      .on_click((_e, cx) => {
        cx.stop_propagation();
        run(command, args);
      })
      .child(MC[icon] ? image(`mods/mc-status/art/icons/${MC[icon]}.svg`).size(15) : svg(`mods/mc-pane/${icon}.svg`).size(14));
  }

  render(cx) {
    const t = theme();
    const p = this.me();
    if (!p) return div();
    const name = p.name || ((p.program?.agent || p.program?.shell) && p.program.name) || p.title || p.program?.name || "shell";
    const pic = p.program?.agent && p.terminal ? image(`${CATS}/${coatOf(p.terminal)}-face-sm.png`).w(17).h(17).flex_none() : icon(p.program, 14, t.dim);
    const st = p.status;
    const pane = p.pane;
    const bottom = paneFrame(layout())?.header?.position === "bottom";
    return h_flex()
      .id(`pane-head-${pane}`)
      .size_full()
      .px(10)
      .gap(8)
      .items_center()
      .bg("#16171ccc")
      .when(bottom, el => el.border_t(1))
      .when(!bottom, el => el.border_b(1))
      .border_color("#000000")
      .text_size(12)
      .on_hover((hovered, cx) => { this.hovered = hovered; cx.notify(); })
      .on_click(() => run("pane.focus", { pane }))
      .when(Boolean(pic), (el) => el.child(pic))
      .child(div().flex_none().truncate().max_w(260).font_medium().text_color(t.foreground).child(name))
      .child(div().flex_1().truncate().text_color(t.dim).child(folder(p.cwd)))
      .when(st === "working", el => el.child(h_flex().flex_none().gap(4).items_center().text_size(10.5).text_color(t.working).child(image("mods/mc-status/art/torch.svg").size(15)).child("working")))
      .when(st === "blocked", el => el.child(h_flex().flex_none().gap(4).items_center().text_size(10.5).text_color(t.blocked).child(image("mods/mc-status/art/gift.svg").size(16)).child("Needs you")))
      .when(st === "done", el => el.child(h_flex().flex_none().gap(4).items_center().text_size(10.5).text_color(t.done).child(image("mods/mc-status/art/xp.svg").size(16)).child("done")))
      .when(this.hovered, el => el
        .child(this.button(t, `ph-r-${pane}`, "split-right", "pane.split", { direction: "right", pane }))
        .child(this.button(t, `ph-d-${pane}`, "split-down", "pane.split", { direction: "down", pane }))
        .child(this.button(t, `ph-z-${pane}`, p.zoomed ? "unzoom" : "zoom", "pane.zoom", { pane }))
        .child(this.button(t, `ph-x-${pane}`, "close", "pane.close", { pane })));
  }
}
