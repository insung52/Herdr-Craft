import { View, div, image, svg } from "gpui-kit";
import { h_flex, v_flex } from "gpui-base";
import { theme, run, props, window, shared, setShared, updates, layout } from "herdr";

// Minecraft stone button look: black outline (white when selected), light top edge, dark bottom edge,
// grey face that turns blue-grey under the pointer. `el` must not set its own bg/border.
const STONE = { face: "#6f6f6f", hover: "#7d85b8", hi: "#a9a9a9", lo: "#3f3f3f", text: "#ffffff", sub: "#dcdcdc" };
function stone(el, on = false) {
  return el.relative().border(1).border_color(on ? "#ffffff" : "#000000").bg(on ? "#7a7a7a" : STONE.face)
    .hover((s) => s.bg(STONE.hover))
    .child(div().absolute().left(0).right(0).top(0).h(2).bg(STONE.hi))
    .child(div().absolute().left(0).right(0).bottom(0).h(2).bg(STONE.lo));
}

function find(node, id) {
  if (node?.id === id) return node;
  for (const child of node?.children ?? []) {
    const found = find(child, id);
    if (found) return found;
  }
  return null;
}

// The sidebar's rail goes by its width, not a flag: dragging its edge narrows it too.
const narrow = () => (find(layout(), "sidebar")?.size?.px ?? Infinity) < 160;

// To the rail (on macOS wide enough for the traffic lights), or back to the width it had.
function toggleSidebar() {
  const width = find(layout(), "sidebar")?.size?.px;
  if (!narrow()) setShared("sidebar.width", width);
  // Mods edited before the rail went by width still read the flag.
  setShared("sidebar.collapsed", !narrow());
  run("layout.resize", { id: "sidebar", px: narrow() ? (shared("sidebar.width") ?? 268) : window()?.platform === "macos" ? 76 : 44 });
}

export default class WorkspaceChrome extends View {
  button(id, label, action) {
    const t = theme();
    return stone(div().id(id).size(24).ml(3).flex_none().flex().items_center().justify_center().text_color(STONE.text))
      .on_mouse_down("left", (_e, cx) => cx.stop_propagation()).on_click(action).child(label);
  }
  render() {
    const t = theme();
    const collapsed = narrow();
    if (props()?.footer) {
      const row = (id, icon, label, dim, action) => stone(h_flex().id(id).h(26).mb(3).px(8).gap(9).items_center())
        .when(collapsed, el => el.w(32).px(0).justify_center().tooltip(label))
        .text_color(STONE.text).cursor_pointer()
        .on_click(action).child(icon.endsWith(".svg") ? image(`mods/mc-status/art/icons/${icon}`).size(16) : svg(`mods/mc-chrome/${icon}.svg`).size(14))
        .when(!collapsed, el => el.child(label));
      const ready = div().size(6).rounded_full().bg(t.accent);
      return v_flex().size_full().border_t(1).border_color(t.border).px(8).pt(4).pb(8).text_size(13)
        .when(collapsed, el => el.px(0).items_center())
        .child(row("settings", "crafting-table.svg", "Settings", false, () => run("app.settings"))
          .when(Boolean(updates().app.ready), el => el.child(collapsed ? ready.absolute().top(5).right(6) : ready)))
        .child(row("machine", "nether-portal.svg", "Add machine", true, () => run("mod.open", { name: "machine-add" })));
    }
    return h_flex().size_full().pl(collapsed ? 6 : 14).pr(10).gap(4).items_center().text_size(13.5)
      .when(window()?.platform === "macos" && !window()?.fullscreen && !collapsed, el => el.pl(76))
      .when(!collapsed, el => el.child(h_flex().flex_1().gap(8).items_center().child(image("mods/mc-status/art/beacon.svg").size(22)).child(div().font_semibold().text_color(t.foreground).child("Herdr")).child(div().text_size(10.5).text_color(t.accent).child("craft"))))
      .when(!collapsed, el => el.child(this.button("search", image("mods/mc-status/art/icons/spyglass.svg").size(16), () => run("mod.open", { name: "picker" }))))
      // On the macOS rail the traffic lights fill the row; the agents list's » unfolds it.
      .when(!(collapsed && window()?.platform === "macos"), el => el.child(this.button("sidebar-toggle", image("mods/mc-status/art/icons/map.svg").size(16), toggleSidebar)));
  }
}
