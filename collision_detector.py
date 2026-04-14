#!/usr/bin/env python3
"""
Collision Detector — Equipos Educativos
Detects teachers shared between class groups (level + letter) and shows them
grouped by the number of shared teachers, from fewest to most.
"""

import json
import os
import tkinter as tk
from collections import defaultdict
from itertools import combinations
from tkinter import filedialog, messagebox, ttk


# ── Data processing ────────────────────────────────────────────────────────────

def _normalize_name(name: str) -> str:
    """Collapse internal whitespace so 'Doe, John' == 'Doe,  John'."""
    return " ".join(name.split())


def load_json(filepath: str) -> list:
    with open(filepath, "r", encoding="utf-8") as fh:
        return json.load(fh)


def compute_collisions(data: list) -> dict:
    """
    For every pair of (level, group) keys find the set of shared teacher names.

    Returns
    -------
    dict mapping  (group_key_1, group_key_2) -> sorted list of teacher names
    where group_key = (level_string, group_letter_string)
    """
    group_teachers: dict[tuple, set] = {}
    for level_entry in data:
        level = level_entry["level"]
        for grp_name, grp_data in level_entry["groups"].items():
            teachers = {_normalize_name(t["name"]) for t in grp_data["teachers"]}
            group_teachers[(level, grp_name)] = teachers

    result: dict[tuple, list] = {}
    groups = list(group_teachers.keys())
    for g1, g2 in combinations(groups, 2):
        shared = sorted(group_teachers[g1] & group_teachers[g2])
        result[(g1, g2)] = shared
    return result


# ── Application ────────────────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Detector de Colisiones — Equipos Educativos")
        self.geometry("1280x760")
        self.minsize(900, 520)
        self._collision_map: dict[str, tuple] = {}  # tree_item_id -> (g1, g2, teachers)
        self._setup_styles()
        self._build_ui()
        self._show_placeholder()

    # ── Styles ─────────────────────────────────────────────────────────────────

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TLabelframe.Label", font=("Helvetica", 10, "bold"), foreground="#2c3e50")
        style.configure("Treeview", font=("Helvetica", 10), rowheight=28)
        style.map(
            "Treeview",
            background=[("selected", "#3498db")],
            foreground=[("selected", "white")],
        )

    # ── UI construction ─────────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_header()
        self._build_main_area()

    def _build_header(self):
        header = tk.Frame(self, bg="#2c3e50", pady=10)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="Detector de Colisiones — Equipos Educativos",
            bg="#2c3e50", fg="white",
            font=("Helvetica", 14, "bold"),
        ).pack(side=tk.LEFT, padx=16)

        load_btn = tk.Button(
            header,
            text="  Cargar JSON  ",
            command=self._load_file,
            bg="#27ae60", fg="white",
            font=("Helvetica", 10, "bold"),
            relief=tk.FLAT, cursor="hand2",
            padx=8, pady=4,
        )
        load_btn.pack(side=tk.RIGHT, padx=16)

        self._file_lbl = tk.Label(
            header,
            text="Ningún archivo cargado",
            bg="#2c3e50", fg="#95a5a6",
            font=("Helvetica", 9),
        )
        self._file_lbl.pack(side=tk.RIGHT)

    def _build_main_area(self):
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ── Left panel: tree ────────────────────────────────────────────────────
        left = ttk.LabelFrame(
            paned,
            text="Colisiones agrupadas por número de profesores compartidos",
            padding=4,
        )
        paned.add(left, weight=3)

        self._tree = ttk.Treeview(left, show="tree", selectmode="browse")
        self._tree.tag_configure(
            "group",
            font=("Helvetica", 10, "bold"),
            foreground="#1a252f",
        )
        self._tree.tag_configure("pair", font=("Helvetica", 10))

        vsb_tree = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self._tree.yview)
        hsb_tree = ttk.Scrollbar(left, orient=tk.HORIZONTAL, command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb_tree.set, xscrollcommand=hsb_tree.set)

        self._tree.grid(row=0, column=0, sticky="nsew")
        vsb_tree.grid(row=0, column=1, sticky="ns")
        hsb_tree.grid(row=1, column=0, sticky="ew")
        left.rowconfigure(0, weight=1)
        left.columnconfigure(0, weight=1)

        self._tree.bind("<<TreeviewSelect>>", self._on_select)

        # ── Right panel: detail ─────────────────────────────────────────────────
        right = ttk.LabelFrame(
            paned,
            text="Profesores que provocan la colisión",
            padding=6,
        )
        paned.add(right, weight=2)

        self._detail = tk.Text(
            right,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Helvetica", 11),
            bg="#fdfefe",
            relief=tk.FLAT,
            padx=14,
            pady=14,
        )
        vsb_detail = ttk.Scrollbar(right, orient=tk.VERTICAL, command=self._detail.yview)
        self._detail.configure(yscrollcommand=vsb_detail.set)

        self._detail.grid(row=0, column=0, sticky="nsew")
        vsb_detail.grid(row=0, column=1, sticky="ns")
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)

        # Text styling tags
        self._detail.tag_configure(
            "title",
            font=("Helvetica", 12, "bold"),
            foreground="#2c3e50",
            spacing3=4,
        )
        self._detail.tag_configure(
            "subtitle",
            font=("Helvetica", 10),
            foreground="#7f8c8d",
            spacing3=10,
        )
        self._detail.tag_configure(
            "teacher",
            font=("Helvetica", 11),
            foreground="#2c3e50",
            lmargin1=6,
            lmargin2=6,
            spacing1=3,
        )
        self._detail.tag_configure(
            "hint",
            font=("Helvetica", 10, "italic"),
            foreground="#95a5a6",
        )

    # ── File loading ────────────────────────────────────────────────────────────

    def _load_file(self):
        filepath = filedialog.askopenfilename(
            title="Seleccionar archivo de equipos educativos",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not filepath:
            return
        try:
            data = load_json(filepath)
            collisions = compute_collisions(data)
            self._populate_tree(collisions)
            self._file_lbl.config(text=os.path.basename(filepath))
        except Exception as exc:
            messagebox.showerror("Error al cargar", f"No se pudo procesar el archivo:\n{exc}")

    # ── Tree population ─────────────────────────────────────────────────────────

    def _populate_tree(self, collisions: dict):
        for item in self._tree.get_children():
            self._tree.delete(item)
        self._collision_map.clear()
        self._show_placeholder()

        by_count: dict[int, list] = defaultdict(list)
        for (g1, g2), teachers in collisions.items():
            by_count[len(teachers)].append((g1, g2, teachers))

        for count in sorted(by_count.keys()):
            entries = sorted(
                by_count[count],
                key=lambda e: (e[0][0], e[0][1], e[1][0], e[1][1]),
            )
            n = len(entries)
            pairs_label = f"{n} par{'es' if n != 1 else ''}"
            if count == 0:
                header = f"Sin colisiones  —  {pairs_label}"
            elif count == 1:
                header = f"1 colisión  —  {pairs_label}"
            else:
                header = f"{count} colisiones  —  {pairs_label}"

            # Collapse the "no collisions" group to keep the view clean
            parent = self._tree.insert(
                "", "end",
                text=f"  {header}",
                tags=("group",),
                open=(count > 0),
            )

            for g1, g2, teachers in entries:
                label = f"    {g1[0]} / {g1[1]}   ↔   {g2[0]} / {g2[1]}"
                iid = self._tree.insert(parent, "end", text=label, tags=("pair",))
                self._collision_map[iid] = (g1, g2, teachers)

    # ── Selection handler ───────────────────────────────────────────────────────

    def _on_select(self, _event):
        sel = self._tree.selection()
        if not sel:
            return
        iid = sel[0]
        if iid not in self._collision_map:
            # A group header was clicked — clear detail
            self._show_placeholder()
            return
        g1, g2, teachers = self._collision_map[iid]
        self._show_detail(g1, g2, teachers)

    # ── Detail panel helpers ────────────────────────────────────────────────────

    def _write_detail(self, *segments: tuple):
        """Write (text, tag_or_None) segments into the read-only detail widget."""
        self._detail.config(state=tk.NORMAL)
        self._detail.delete("1.0", tk.END)
        for text, tag in segments:
            self._detail.insert(tk.END, text, tag) if tag else self._detail.insert(tk.END, text)
        self._detail.config(state=tk.DISABLED)

    def _show_placeholder(self):
        self._write_detail(
            ("Selecciona un par de grupos para ver\nlos profesores en colisión.", "hint"),
        )

    def _show_detail(self, g1: tuple, g2: tuple, teachers: list):
        title = f"{g1[0]} / {g1[1]}   ↔   {g2[0]} / {g2[1]}\n"
        if teachers:
            n = len(teachers)
            subtitle = f"{n} profesor{'es' if n != 1 else ''} compartido{'s' if n != 1 else ''}:\n\n"
            teacher_segments = [(f"• {t}\n", "teacher") for t in teachers]
            self._write_detail(
                (title, "title"),
                (subtitle, "subtitle"),
                *teacher_segments,
            )
        else:
            self._write_detail(
                (title, "title"),
                ("Sin profesores compartidos entre estos grupos.", "hint"),
            )


# ── Entry point ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = App()
    app.mainloop()
