import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import json
from datetime import datetime

# ─────────────────────────────────────────────
#  THEME CONSTANTS
# ─────────────────────────────────────────────
DARK = {
    "bg":        "#0d1117",
    "panel":     "#161b22",
    "border":    "#30363d",
    "text":      "#e6edf3",
    "muted":     "#8b949e",
    "green":     "#3fb950",
    "blue":      "#58a6ff",
    "orange":    "#d29922",
    "red":       "#f85149",
    "entry_bg":  "#21262d",
    "entry_fg":  "#e6edf3",
    "btn":       "#21262d",
    "btn_hover": "#30363d",
    "header":    "#58a6ff",
}

LIGHT = {
    "bg":        "#f6f8fa",
    "panel":     "#ffffff",
    "border":    "#d0d7de",
    "text":      "#24292f",
    "muted":     "#57606a",
    "green":     "#1a7f37",
    "blue":      "#0969da",
    "orange":    "#9a6700",
    "red":       "#cf222e",
    "entry_bg":  "#ffffff",
    "entry_fg":  "#24292f",
    "btn":       "#f6f8fa",
    "btn_hover": "#eaeef2",
    "header":    "#0969da",
}

PRESETS = {
    "Safe State (Banker's)": {
        "mode": "banker",
        "processes": 5,
        "resources": 3,
        "allocation": [[0,1,0],[2,0,0],[3,0,2],[2,1,1],[0,0,2]],
        "max":        [[7,5,3],[3,2,2],[9,0,2],[2,2,2],[4,3,3]],
        "total":      [10, 5, 7],
    },
    "Unsafe State (Banker's)": {
        "mode": "banker",
        "processes": 4,
        "resources": 2,
        "allocation": [[1,0],[0,2],[3,0],[2,1]],
        "max":        [[2,1],[1,3],[4,1],[3,2]],
        "total":      [4, 4],
    },
    "Deadlock Detected": {
        "mode": "detection",
        "processes": 3,
        "resources": 2,
        "allocation": [[1,0],[0,1],[0,0]],
        "request":    [[0,1],[1,0],[0,0]],
        "total":      [1, 1],
    },
    "No Deadlock (Detection)": {
        "mode": "detection",
        "processes": 4,
        "resources": 3,
        "allocation": [[0,1,0],[2,0,0],[3,0,3],[2,1,1]],
        "request":    [[0,0,0],[2,0,2],[0,0,0],[1,0,0]],
        "total":      [7, 2, 6],
    },
}


class DeadlockSimulator:

    def __init__(self, root):
        self.root = root
        self.root.title("Deadlock Analysis Simulator")
        self.root.state("zoomed")

        self.mode        = tk.StringVar(value="banker")
        self.theme_name  = tk.StringVar(value="dark")
        self.T           = DARK  # active theme dict

        self.allocation_entries = []
        self.request_entries    = []
        self.max_entries        = []
        self.total_entries      = []
        self.need_labels        = []   # read-only need matrix display

        self.deadlocked_processes = []
        self.step_queue           = []   # for step-by-step mode
        self.step_mode            = tk.BooleanVar(value=False)
        self.animation_running    = False

        self._setup_fonts()
        self._setup_styles()
        self.setup_ui()

    # ─────────────────────────────────────────
    #  FONTS & STYLES
    # ─────────────────────────────────────────

    def _setup_fonts(self):
        import tkinter.font as tkfont
        self.font_mono  = ("Consolas", 10)
        self.font_label = ("Segoe UI", 10)
        self.font_head  = ("Segoe UI Semibold", 11)
        self.font_title = ("Segoe UI Semibold", 13)

    def _setup_styles(self):
        T = self.T
        s = ttk.Style()
        s.theme_use("clam")

        s.configure("TFrame",       background=T["bg"])
        s.configure("Panel.TFrame", background=T["panel"],
                    relief="flat", borderwidth=1)
        s.configure("TLabel",       background=T["bg"],
                    foreground=T["text"],
                    font=self.font_label)
        s.configure("Head.TLabel",  background=T["panel"],
                    foreground=T["header"],
                    font=self.font_head)
        s.configure("Muted.TLabel", background=T["bg"],
                    foreground=T["muted"],
                    font=("Segoe UI", 9))
        s.configure("TRadiobutton", background=T["bg"],
                    foreground=T["text"],
                    font=self.font_label)
        s.configure("TCheckbutton", background=T["bg"],
                    foreground=T["text"],
                    font=self.font_label)
        s.configure("TEntry",
                    fieldbackground=T["entry_bg"],
                    foreground=T["entry_fg"],
                    insertcolor=T["text"],
                    bordercolor=T["border"],
                    lightcolor=T["border"],
                    darkcolor=T["border"],
                    font=self.font_mono)
        s.configure("TButton",
                    background=T["btn"],
                    foreground=T["text"],
                    bordercolor=T["border"],
                    font=self.font_label,
                    padding=(8, 4))
        s.map("TButton",
              background=[("active", T["btn_hover"])],
              foreground=[("active", T["text"])])

        # Accent buttons
        s.configure("Green.TButton",
                    background=T["green"],
                    foreground="#ffffff",
                    font=("Segoe UI Semibold", 10),
                    padding=(10, 5))
        s.map("Green.TButton",
              background=[("active", "#2ea043")])
        s.configure("Red.TButton",
                    background=T["red"],
                    foreground="#ffffff",
                    font=("Segoe UI Semibold", 10),
                    padding=(10, 5))
        s.map("Red.TButton",
              background=[("active", "#da3633")])
        s.configure("Blue.TButton",
                    background=T["blue"],
                    foreground="#ffffff",
                    font=("Segoe UI Semibold", 10),
                    padding=(10, 5))
        s.map("Blue.TButton",
              background=[("active", "#388bfd")])

        s.configure("TCombobox",
                    fieldbackground=T["entry_bg"],
                    background=T["entry_bg"],
                    foreground=T["entry_fg"],
                    arrowcolor=T["text"],
                    selectbackground=T["entry_bg"],
                    selectforeground=T["entry_fg"])

    def _apply_theme(self):
        self.T = DARK if self.theme_name.get() == "dark" else LIGHT
        self._setup_styles()
        self._repaint_widgets(self.root)
        self._redraw_plot_bg()

    def _repaint_widgets(self, widget):
        T = self.T
        cls = widget.__class__.__name__
        try:
            if cls == "Text":
                widget.config(bg=T["panel"], fg=T["text"],
                               insertbackground=T["text"])
            elif cls == "Canvas":
                widget.config(bg=T["bg"])
        except Exception:
            pass
        for child in widget.winfo_children():
            self._repaint_widgets(child)

    def _redraw_plot_bg(self):
        T = self.T
        bg = T["bg"]
        self.figure.patch.set_facecolor(bg)
        self.ax.set_facecolor(bg)
        self.canvas.draw()

    # ─────────────────────────────────────────
    #  UI LAYOUT
    # ─────────────────────────────────────────

    def setup_ui(self):
        T = self.T
        self.root.configure(bg=T["bg"])

        # ── Title bar ──
        title_bar = tk.Frame(self.root, bg=T["panel"], height=50)
        title_bar.pack(fill="x")
        tk.Label(title_bar, text="⬡ DEADLOCK ANALYSIS SIMULATOR",
                 bg=T["panel"], fg=T["header"],
                 font=("Consolas", 14, "bold")).pack(side="left", padx=15, pady=10)
        tk.Label(title_bar, text="Resource Allocation & Deadlock Detection",
                 bg=T["panel"], fg=T["muted"],
                 font=("Segoe UI", 9)).pack(side="left", padx=5, pady=10)

        # Theme toggle
        tk.Button(title_bar, text="☀ Light" if self.theme_name.get() == "dark" else "● Dark",
                  bg=T["btn"], fg=T["text"], relief="flat",
                  font=("Segoe UI", 9),
                  command=self._toggle_theme,
                  cursor="hand2").pack(side="right", padx=15, pady=10)

        sep = tk.Frame(self.root, bg=T["border"], height=1)
        sep.pack(fill="x")

        # ── Control bar ──
        ctrl = tk.Frame(self.root, bg=T["panel"], pady=8)
        ctrl.pack(fill="x")

        self._ctrl_bar = ctrl  # for theme re-paint reference

        def lbl(text, parent=ctrl):
            return tk.Label(parent, text=text,
                            bg=T["panel"], fg=T["muted"],
                            font=("Segoe UI", 9))

        lbl("MODE").pack(side="left", padx=(15, 4))
        for val, txt in [("banker", "Banker's Algorithm"),
                         ("detection", "Deadlock Detection")]:
            rb = ttk.Radiobutton(ctrl, text=txt,
                                 variable=self.mode, value=val,
                                 command=self.refresh_matrices)
            rb.pack(side="left", padx=4)

        tk.Frame(ctrl, bg=T["border"], width=1).pack(side="left",
                                                      fill="y", padx=10, pady=4)

        lbl("PROCESSES").pack(side="left", padx=(0, 4))
        self.process_entry = ttk.Entry(ctrl, width=4)
        self.process_entry.pack(side="left")

        lbl("  RESOURCES").pack(side="left", padx=(8, 4))
        self.resource_entry = ttk.Entry(ctrl, width=4)
        self.resource_entry.pack(side="left")

        tk.Frame(ctrl, bg=T["border"], width=1).pack(side="left",
                                                      fill="y", padx=10, pady=4)

        lbl("PRESET").pack(side="left", padx=(0, 4))
        self.preset_var = tk.StringVar(value="— Select —")
        preset_cb = ttk.Combobox(ctrl, textvariable=self.preset_var,
                                 values=["— Select —"] + list(PRESETS.keys()),
                                 width=24, state="readonly")
        preset_cb.pack(side="left")
        preset_cb.bind("<<ComboboxSelected>>", self._load_preset)

        tk.Frame(ctrl, bg=T["border"], width=1).pack(side="left",
                                                      fill="y", padx=10, pady=4)

        ttk.Button(ctrl, text="Generate",
                   command=self.generate_matrices).pack(side="left", padx=3)
        ttk.Button(ctrl, text="Random Fill",
                   command=self.random_fill).pack(side="left", padx=3)

        tk.Frame(ctrl, bg=T["border"], width=1).pack(side="left",
                                                      fill="y", padx=10, pady=4)

        ttk.Button(ctrl, text="▶  Run",
                   style="Green.TButton",
                   command=self.run_algorithm).pack(side="left", padx=3)

        ttk.Checkbutton(ctrl, text="Step-by-Step",
                        variable=self.step_mode).pack(side="left", padx=6)

        self.next_btn = ttk.Button(ctrl, text="Next Step ▶",
                                   style="Blue.TButton",
                                   command=self._advance_step,
                                   state="disabled")
        self.next_btn.pack(side="left", padx=3)

        ttk.Button(ctrl, text="⟳ Reset",
                   style="Red.TButton",
                   command=self.reset_all).pack(side="right", padx=15)
        ttk.Button(ctrl, text="⬇ Export Log",
                   command=self.export_log).pack(side="right", padx=3)

        sep2 = tk.Frame(self.root, bg=T["border"], height=1)
        sep2.pack(fill="x")

        # ── Main content ──
        content = tk.Frame(self.root, bg=T["bg"])
        content.pack(fill="both", expand=True, padx=0, pady=0)

        # Left: matrices
        left_wrap = tk.Frame(content, bg=T["bg"])
        left_wrap.pack(side="left", fill="both", expand=False,
                       padx=10, pady=10)

        self.matrix_canvas = tk.Canvas(left_wrap, bg=T["bg"],
                                       highlightthickness=0)
        self.matrix_scroll = ttk.Scrollbar(left_wrap, orient="vertical",
                                           command=self.matrix_canvas.yview)
        self.matrix_canvas.configure(yscrollcommand=self.matrix_scroll.set)
        self.matrix_scroll.pack(side="right", fill="y")
        self.matrix_canvas.pack(side="left", fill="both", expand=True)

        self.matrix_frame = tk.Frame(self.matrix_canvas, bg=T["bg"])
        self.matrix_canvas.create_window((0, 0), window=self.matrix_frame,
                                          anchor="nw")
        self.matrix_frame.bind("<Configure>", lambda e:
            self.matrix_canvas.configure(
                scrollregion=self.matrix_canvas.bbox("all")))

        # Right: graph + log + stats
        right = tk.Frame(content, bg=T["bg"])
        right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Graph
        self.figure = plt.Figure(figsize=(6, 4.5), facecolor=T["bg"])
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor(T["bg"])
        self.figure.tight_layout(pad=2)

        graph_frame = tk.Frame(right, bg=T["panel"],
                               highlightthickness=1,
                               highlightbackground=T["border"])
        graph_frame.pack(fill="both", expand=True)

        self.canvas = FigureCanvasTkAgg(self.figure, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Stats bar
        self.stats_frame = tk.Frame(right, bg=T["panel"],
                                    highlightthickness=1,
                                    highlightbackground=T["border"])
        self.stats_frame.pack(fill="x", pady=(4, 0))
        self.stats_label = tk.Label(self.stats_frame,
                                    text="Stats will appear after running.",
                                    bg=T["panel"], fg=T["muted"],
                                    font=("Consolas", 9),
                                    anchor="w")
        self.stats_label.pack(fill="x", padx=8, pady=4)

        # Log
        log_outer = tk.Frame(right, bg=T["panel"],
                             highlightthickness=1,
                             highlightbackground=T["border"])
        log_outer.pack(fill="x", pady=(4, 0))

        log_header = tk.Frame(log_outer, bg=T["panel"])
        log_header.pack(fill="x")
        tk.Label(log_header, text="EXECUTION LOG",
                 bg=T["panel"], fg=T["header"],
                 font=("Consolas", 9, "bold")).pack(side="left", padx=8, pady=4)
        ttk.Button(log_header, text="Clear",
                   command=lambda: self.log_box.delete(1.0, tk.END)).pack(
                       side="right", padx=6, pady=2)

        self.log_box = tk.Text(log_outer, height=9,
                               bg=T["panel"], fg=T["text"],
                               font=("Consolas", 9),
                               relief="flat", padx=8, pady=4,
                               insertbackground=T["text"])
        self.log_box.pack(fill="x")

        # Log colour tags
        self.log_box.tag_config("ok",    foreground=T["green"])
        self.log_box.tag_config("warn",  foreground=T["orange"])
        self.log_box.tag_config("err",   foreground=T["red"])
        self.log_box.tag_config("info",  foreground=T["blue"])
        self.log_box.tag_config("muted", foreground=T["muted"])

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Frame(self.root, bg=T["panel"], height=24)
        status_bar.pack(fill="x", side="bottom")
        tk.Label(status_bar, textvariable=self.status_var,
                 bg=T["panel"], fg=T["muted"],
                 font=("Consolas", 8),
                 anchor="w").pack(side="left", padx=10, pady=2)
        self.clock_label = tk.Label(status_bar, text="",
                                    bg=T["panel"], fg=T["muted"],
                                    font=("Consolas", 8))
        self.clock_label.pack(side="right", padx=10)
        self._tick_clock()

    def _tick_clock(self):
        self.clock_label.config(
            text=datetime.now().strftime("%H:%M:%S"))
        self.root.after(1000, self._tick_clock)

    def _toggle_theme(self):
        self.theme_name.set(
            "light" if self.theme_name.get() == "dark" else "dark")
        self._apply_theme()
        # Rebuild UI to fully repaint (simpler than tracking every widget)
        # Just rebuild title bar btn text:
        # (full rebuild is too expensive; we rely on _apply_theme)

    def _set_status(self, msg, tag="muted"):
        self.status_var.set(msg)

    # ─────────────────────────────────────────
    #  MATRIX GENERATION
    # ─────────────────────────────────────────

    def _matrix_section_label(self, parent, text, row, col, colspan,
                               color=None):
        T = self.T
        fg = color or T["header"]
        tk.Label(parent, text=text,
                 bg=T["bg"], fg=fg,
                 font=("Segoe UI Semibold", 10)).grid(
                     row=row, column=col, columnspan=colspan,
                     padx=4, pady=(8, 2), sticky="w")

    def _col_header(self, parent, text, row, col):
        T = self.T
        tk.Label(parent, text=text,
                 bg=T["bg"], fg=T["muted"],
                 font=("Consolas", 9)).grid(row=row, column=col, padx=3)

    def _row_label(self, parent, text, row, col):
        T = self.T
        tk.Label(parent, text=text,
                 bg=T["bg"], fg=T["text"],
                 font=("Consolas", 10, "bold")).grid(
                     row=row, column=col, padx=6, pady=2, sticky="e")

    def _make_entry(self, parent, row, col, width=4):
        T = self.T
        var = tk.StringVar(value="0")
        e = tk.Entry(parent, textvariable=var, width=width,
                     bg=T["entry_bg"], fg=T["entry_fg"],
                     insertbackground=T["text"],
                     relief="flat",
                     font=("Consolas", 10),
                     justify="center",
                     highlightthickness=1,
                     highlightbackground=T["border"],
                     highlightcolor=T["blue"])
        e.grid(row=row, column=col, padx=3, pady=3)
        return e

    def generate_matrices(self):
        for w in self.matrix_frame.winfo_children():
            w.destroy()
        self.allocation_entries = []
        self.request_entries    = []
        self.max_entries        = []
        self.total_entries      = []
        self.need_labels        = []

        try:
            n = int(self.process_entry.get())
            m = int(self.resource_entry.get())
            if not (1 <= n <= 10 and 1 <= m <= 8):
                raise ValueError
        except Exception:
            messagebox.showerror("Input Error",
                                 "Processes: 1–10, Resources: 1–8")
            return

        T = self.T
        f = self.matrix_frame
        cur_col = 0

        # ── ALLOCATION ──
        self._matrix_section_label(f, "ALLOCATION", 0, cur_col, m + 1)
        self._row_label(f, "", 1, cur_col)
        for j in range(m):
            self._col_header(f, f"R{j}", 1, cur_col + 1 + j)
        for i in range(n):
            self._row_label(f, f"P{i}", i + 2, cur_col)
            row = []
            for j in range(m):
                e = self._make_entry(f, i + 2, cur_col + 1 + j)
                row.append(e)
            self.allocation_entries.append(row)

        cur_col += m + 2

        # ── SEPARATOR ──
        tk.Frame(f, bg=T["border"], width=2).grid(
            row=0, column=cur_col - 1, rowspan=n + 3, sticky="ns", padx=2)

        # ── MAX / REQUEST ──
        if self.mode.get() == "banker":
            self._matrix_section_label(f, "MAX CLAIM", 0, cur_col, m + 1,
                                        color=T["green"])
            self._row_label(f, "", 1, cur_col)
            for j in range(m):
                self._col_header(f, f"R{j}", 1, cur_col + 1 + j)
            for i in range(n):
                self._row_label(f, f"P{i}", i + 2, cur_col)
                row = []
                for j in range(m):
                    e = self._make_entry(f, i + 2, cur_col + 1 + j)
                    row.append(e)
                self.max_entries.append(row)
        else:
            self._matrix_section_label(f, "REQUEST", 0, cur_col, m + 1,
                                        color=T["orange"])
            self._row_label(f, "", 1, cur_col)
            for j in range(m):
                self._col_header(f, f"R{j}", 1, cur_col + 1 + j)
            for i in range(n):
                self._row_label(f, f"P{i}", i + 2, cur_col)
                row = []
                for j in range(m):
                    e = self._make_entry(f, i + 2, cur_col + 1 + j)
                    row.append(e)
                self.request_entries.append(row)

        cur_col += m + 2

        # ── NEED (read-only, Banker's only) ──
        if self.mode.get() == "banker":
            tk.Frame(f, bg=T["border"], width=2).grid(
                row=0, column=cur_col - 1, rowspan=n + 3, sticky="ns", padx=2)
            self._matrix_section_label(f, "NEED (max−alloc)", 0,
                                        cur_col, m + 1, color=T["muted"])
            self._row_label(f, "", 1, cur_col)
            for j in range(m):
                self._col_header(f, f"R{j}", 1, cur_col + 1 + j)
            for i in range(n):
                self._row_label(f, f"P{i}", i + 2, cur_col)
                row_lbl = []
                for j in range(m):
                    lbl = tk.Label(f, text="—", width=4,
                                   bg=T["entry_bg"], fg=T["muted"],
                                   font=("Consolas", 10),
                                   relief="flat")
                    lbl.grid(row=i + 2, column=cur_col + 1 + j,
                             padx=3, pady=3)
                    row_lbl.append(lbl)
                self.need_labels.append(row_lbl)
            cur_col += m + 2

        # ── TOTAL RESOURCES ──
        tk.Frame(f, bg=T["border"], width=2).grid(
            row=0, column=cur_col - 1, rowspan=n + 3, sticky="ns", padx=2)
        self._matrix_section_label(f, "TOTAL RESOURCES", n + 3,
                                    cur_col, m + 2)
        for j in range(m):
            self._col_header(f, f"R{j}", n + 4, cur_col + j)
        for j in range(m):
            e = self._make_entry(f, n + 5, cur_col + j)
            self.total_entries.append(e)

        # ── Bind live need update (Banker's) ──
        if self.mode.get() == "banker":
            self._bind_need_update(n, m)

        self._set_status(f"Matrix generated: {n} processes × {m} resources")

    def _bind_need_update(self, n, m):
        def update(*_):
            for i in range(n):
                for j in range(m):
                    try:
                        a = int(self.allocation_entries[i][j].get())
                        mx = int(self.max_entries[i][j].get())
                        need = mx - a
                        color = self.T["orange"] if need < 0 else self.T["text"]
                        self.need_labels[i][j].config(
                            text=str(need), fg=color)
                    except Exception:
                        self.need_labels[i][j].config(text="—",
                                                       fg=self.T["muted"])
        for i in range(n):
            for j in range(m):
                self.allocation_entries[i][j].bind("<KeyRelease>", update)
                self.max_entries[i][j].bind("<KeyRelease>", update)

    def refresh_matrices(self):
        if self.process_entry.get().strip() and self.resource_entry.get().strip():
            self.generate_matrices()

    # ─────────────────────────────────────────
    #  PRESET LOADER
    # ─────────────────────────────────────────

    def _load_preset(self, event=None):
        name = self.preset_var.get()
        if name == "— Select —":
            return
        p = PRESETS[name]
        n, m = p["processes"], p["resources"]

        self.mode.set(p["mode"])
        self.process_entry.delete(0, tk.END)
        self.process_entry.insert(0, str(n))
        self.resource_entry.delete(0, tk.END)
        self.resource_entry.insert(0, str(m))
        self.generate_matrices()

        for i in range(n):
            for j in range(m):
                self.allocation_entries[i][j].delete(0, tk.END)
                self.allocation_entries[i][j].insert(0,
                    str(p["allocation"][i][j]))

        if p["mode"] == "banker":
            for i in range(n):
                for j in range(m):
                    self.max_entries[i][j].delete(0, tk.END)
                    self.max_entries[i][j].insert(0, str(p["max"][i][j]))
        else:
            for i in range(n):
                for j in range(m):
                    self.request_entries[i][j].delete(0, tk.END)
                    self.request_entries[i][j].insert(0,
                        str(p["request"][i][j]))

        for j in range(m):
            self.total_entries[j].delete(0, tk.END)
            self.total_entries[j].insert(0, str(p["total"][j]))

        if self.mode.get() == "banker":
            self._trigger_need_update(n, m)

        self._set_status(f"Preset loaded: {name}")
        self._log(f"[PRESET] Loaded: {name}\n", "info")

    def _trigger_need_update(self, n, m):
        for i in range(n):
            for j in range(m):
                try:
                    a  = int(self.allocation_entries[i][j].get())
                    mx = int(self.max_entries[i][j].get())
                    self.need_labels[i][j].config(text=str(mx - a),
                                                   fg=self.T["text"])
                except Exception:
                    pass

    # ─────────────────────────────────────────
    #  RANDOM FILL
    # ─────────────────────────────────────────

    def random_fill(self):
        if not self.allocation_entries:
            messagebox.showwarning("Warning", "Generate matrices first.")
            return
        try:
            n = int(self.process_entry.get())
            m = int(self.resource_entry.get())
        except Exception:
            return

        # Random total resources
        totals = [random.randint(n, n * 3) for _ in range(m)]
        for j in range(m):
            self.total_entries[j].delete(0, tk.END)
            self.total_entries[j].insert(0, str(totals[j]))

        # Distribute allocation (ensure sum <= total)
        remaining = totals[:]
        allocation = [[0] * m for _ in range(n)]
        for i in range(n):
            for j in range(m):
                hi = min(remaining[j], max(1, totals[j] // n))
                v = random.randint(0, hi)
                allocation[i][j] = v
                remaining[j] -= v

        for i in range(n):
            for j in range(m):
                self.allocation_entries[i][j].delete(0, tk.END)
                self.allocation_entries[i][j].insert(0, str(allocation[i][j]))

        if self.mode.get() == "banker":
            for i in range(n):
                for j in range(m):
                    lo = allocation[i][j]
                    hi = totals[j]
                    mx = random.randint(lo, max(lo, hi))
                    self.max_entries[i][j].delete(0, tk.END)
                    self.max_entries[i][j].insert(0, str(mx))
            self._trigger_need_update(n, m)
        else:
            avail = remaining[:]
            for i in range(n):
                for j in range(m):
                    v = random.randint(0, max(0, avail[j]))
                    self.request_entries[i][j].delete(0, tk.END)
                    self.request_entries[i][j].insert(0, str(v))

        self._set_status("Random values filled.")
        self._log("[RANDOM] Matrix filled with random values.\n", "info")

    # ─────────────────────────────────────────
    #  RESET & EXPORT
    # ─────────────────────────────────────────

    def reset_all(self):
        self.deadlocked_processes = []
        self.step_queue           = []
        self.animation_running    = False
        self.next_btn.config(state="disabled")
        for w in self.matrix_frame.winfo_children():
            w.destroy()
        self.allocation_entries = []
        self.request_entries    = []
        self.max_entries        = []
        self.total_entries      = []
        self.need_labels        = []
        self.process_entry.delete(0, tk.END)
        self.resource_entry.delete(0, tk.END)
        self.log_box.delete(1.0, tk.END)
        self.stats_label.config(text="Stats will appear after running.")
        self.preset_var.set("— Select —")
        self.ax.clear()
        self._redraw_plot_bg()
        self.canvas.draw()
        self._set_status("Reset complete.")

    def export_log(self):
        content = self.log_box.get(1.0, tk.END).strip()
        if not content:
            messagebox.showinfo("Export", "Log is empty.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Export Log")
        if path:
            with open(path, "w") as f:
                f.write(f"Deadlock Simulator — Exported {datetime.now()}\n")
                f.write("=" * 60 + "\n")
                f.write(content)
            self._set_status(f"Log exported: {path}")

    # ─────────────────────────────────────────
    #  LOGGING
    # ─────────────────────────────────────────

    def _log(self, text, tag="muted"):
        self.log_box.insert(tk.END, text, tag)
        self.log_box.see(tk.END)

    # ─────────────────────────────────────────
    #  GRAPH DRAWING
    # ─────────────────────────────────────────

    def draw_graph(self, allocation, request=None,
                   highlight=None, finished=None):
        T = self.T
        self.ax.clear()
        self.ax.set_facecolor(T["bg"])
        self.figure.patch.set_facecolor(T["bg"])

        if finished is None:
            finished = []

        n = len(allocation)
        m = len(allocation[0])

        # ── Dynamic vertical spacing ──────────────────────────────────
        # Give each node at least 1.8 units of vertical space so nodes
        # never overlap regardless of how many processes/resources exist.
        p_spacing = max(1.8, 7.0 / max(n, 1))
        r_spacing = max(1.8, 7.0 / max(m, 1))

        p_height  = (n - 1) * p_spacing
        r_height  = (m - 1) * r_spacing

        # Centre both columns vertically on 0
        G   = nx.DiGraph()
        pos = {}
        for i in range(n):
            G.add_node(f"P{i}")
            pos[f"P{i}"] = (-3.5,  p_height / 2 - i * p_spacing)
        for j in range(m):
            G.add_node(f"R{j}")
            pos[f"R{j}"] = ( 3.5,  r_height / 2 - j * r_spacing)

        # ── Build edges, tracking parallel pairs ─────────────────────
        # A "parallel pair" is when both R→P (allocation) AND P→R
        # (request) exist between the same P and R node.
        alloc_edges   = set()   # (Rj, Pi) that have allocation
        request_edges = set()   # (Pi, Rj) that have request

        for i in range(n):
            if i in finished:
                continue
            for j in range(m):
                if allocation[i][j] > 0:
                    G.add_edge(f"R{j}", f"P{i}",
                               label=str(allocation[i][j]),
                               etype="alloc")
                    alloc_edges.add((f"R{j}", f"P{i}"))

        if request:
            for i in range(n):
                if i in finished:
                    continue
                for j in range(m):
                    if request[i][j] > 0:
                        G.add_edge(f"P{i}", f"R{j}",
                                   label=str(request[i][j]),
                                   etype="req")
                        request_edges.add((f"P{i}", f"R{j}"))

        # Identify pairs that go both ways → need higher curvature
        bidirectional = set()
        for (rj, pi) in alloc_edges:
            if (pi, rj) in request_edges:
                bidirectional.add((rj, pi))
                bidirectional.add((pi, rj))

        # ── Node sizing — shrink when many nodes ─────────────────────
        max_nodes = max(n, m)
        node_size = max(800, int(2800 / max(max_nodes, 1)))
        font_size = max(7,  int(11   - max_nodes * 0.4))

        # ── Draw nodes ───────────────────────────────────────────────
        process_nodes  = [nd for nd in G.nodes() if nd.startswith("P")]
        resource_nodes = [nd for nd in G.nodes() if nd.startswith("R")]

        p_colors = []
        for nd in process_nodes:
            idx = int(nd[1:])
            if idx in self.deadlocked_processes:
                p_colors.append(T["red"])
            elif idx in finished:
                p_colors.append("#3d444d")
            elif highlight is not None and idx == highlight:
                p_colors.append(T["orange"])
            else:
                p_colors.append(T["green"])

        nx.draw_networkx_nodes(G, pos, nodelist=process_nodes,
                               node_color=p_colors,
                               node_size=node_size,
                               node_shape="o", ax=self.ax)
        nx.draw_networkx_nodes(G, pos, nodelist=resource_nodes,
                               node_color=T["blue"],
                               node_size=int(node_size * 1.15),
                               node_shape="s", ax=self.ax)

        # ── Draw edges individually with correct curvature ───────────
        # Bidirectional pairs get opposite curves (rad +0.25 / -0.25)
        # so they arc away from each other and labels don't overlap.
        # Unidirectional edges stay nearly straight (rad 0.05).
        margin = max(12, node_size ** 0.5 * 0.6)

        for u, v, data in G.edges(data=True):
            is_bi  = (u, v) in bidirectional
            etype  = data.get("etype", "alloc")
            if is_bi:
                rad   = 0.28 if etype == "alloc" else -0.28
                color = T["green"] if etype == "alloc" else T["orange"]
                width = 2.2
            else:
                rad   = 0.08
                color = T["muted"]
                width = 1.8

            nx.draw_networkx_edges(
                G, pos,
                edgelist=[(u, v)],
                arrows=True,
                arrowstyle="-|>",
                arrowsize=max(18, node_size // 100),
                width=width,
                edge_color=color,
                connectionstyle=f"arc3,rad={rad}",
                min_source_margin=margin,
                min_target_margin=margin,
                ax=self.ax,
            )

        # ── Labels ───────────────────────────────────────────────────
        nx.draw_networkx_labels(G, pos,
                                font_color=T["bg"],
                                font_size=font_size,
                                font_weight="bold",
                                ax=self.ax)

        # Edge weight labels — offset slightly to avoid sitting on arrows
        edge_labels = nx.get_edge_attributes(G, "label")
        nx.draw_networkx_edge_labels(
            G, pos,
            edge_labels=edge_labels,
            font_color=T["text"],
            font_size=max(7, font_size - 1),
            bbox=dict(boxstyle="round,pad=0.15",
                      fc=T["panel"], ec="none", alpha=0.75),
            ax=self.ax,
        )

        # ── Axis padding so nodes aren't clipped ─────────────────────
        self.ax.set_xlim(-5.5, 5.5)
        y_extent = max(p_height, r_height) / 2 + p_spacing
        self.ax.set_ylim(-y_extent - 0.5, y_extent + 0.5)
        self.ax.axis("off")

        # ── Legend ───────────────────────────────────────────────────
        from matplotlib.patches import Patch, FancyArrow
        legend_elements = [
            Patch(color=T["green"],   label="Active process"),
            Patch(color=T["orange"],  label="Executing / Request edge"),
            Patch(color=T["red"],     label="Deadlocked"),
            Patch(color="#3d444d",    label="Finished"),
            Patch(color=T["blue"],    label="Resource"),
        ]
        self.ax.legend(
            handles=legend_elements,
            loc="lower right",
            facecolor=T["panel"],
            edgecolor=T["border"],
            labelcolor=T["text"],
            fontsize=8,
            framealpha=0.9,
        )

        self.figure.tight_layout(pad=1.2)
        self.canvas.draw()

    # ─────────────────────────────────────────
    #  STATS
    # ─────────────────────────────────────────

    def _show_stats(self, allocation, total, available, mode,
                    safe=None, deadlocked=None):
        n, m = len(allocation), len(total)
        utilization = []
        for j in range(m):
            used = sum(allocation[i][j] for i in range(n))
            pct  = (used / total[j] * 100) if total[j] else 0
            utilization.append(f"R{j}:{pct:.0f}%")

        avail_str = "  ".join(f"R{j}={available[j]}" for j in range(m))
        util_str  = "  ".join(utilization)

        if mode == "banker":
            state = "SAFE ✔" if safe else "UNSAFE ✘"
            color = self.T["green"] if safe else self.T["red"]
        else:
            if deadlocked:
                state = f"DEADLOCK in P{deadlocked}"
                color = self.T["red"]
            else:
                state = "NO DEADLOCK ✔"
                color = self.T["green"]

        self.stats_label.config(
            text=f"  State: {state}   |   Available: {avail_str}   |   "
                 f"Utilization: {util_str}",
            fg=color)

    # ─────────────────────────────────────────
    #  ANIMATION (auto + step modes)
    # ─────────────────────────────────────────

    def animate_execution(self, allocation, sequence,
                          available, request=None,
                          mode="banker", step=0, finished=None):
        if finished is None:
            finished = []

        if step >= len(sequence):
            if mode == "banker":
                self._log("\n🎉 All processes completed — SAFE STATE\n", "ok")
            else:
                self._log("\n🎉 All executable processes completed\n", "ok")
                if not self.deadlocked_processes:
                    self._log("No deadlock detected.\n", "ok")
                else:
                    self._log(
                        f"Deadlock in processes: {self.deadlocked_processes}\n",
                        "err")
            self.animation_running = False
            self.next_btn.config(state="disabled")
            return

        process = sequence[step]
        self._log(f"\n▶  Executing P{process}\n", "info")
        self.draw_graph(allocation, request, highlight=process,
                        finished=finished)
        self._set_status(f"Executing P{process}…")

        def complete():
            for j in range(len(available)):
                available[j] += allocation[process][j]
            finished.append(process)
            label = "Available" if mode == "banker" else "Work"
            self._log(f"  ✔ P{process} done → {label} = {available}\n", "ok")
            self.draw_graph(allocation, request, finished=finished)

            if self.step_mode.get():
                # Queue next step and wait for button click
                self.step_queue = (allocation, sequence, available,
                                   request, mode, step + 1, finished)
                if step + 1 < len(sequence):
                    self.next_btn.config(state="normal")
                else:
                    # Trigger final message
                    self.root.after(200,
                        lambda: self.animate_execution(
                            allocation, sequence,
                            available, request, mode,
                            step + 1, finished))
            else:
                self.root.after(1200,
                    lambda: self.animate_execution(
                        allocation, sequence,
                        available, request, mode,
                        step + 1, finished))

        delay = 0 if self.step_mode.get() else 1200
        self.root.after(delay, complete)

    def _advance_step(self):
        if self.step_queue:
            args = self.step_queue
            self.step_queue = []
            self.next_btn.config(state="disabled")
            self.animate_execution(*args)

    # ─────────────────────────────────────────
    #  RUN
    # ─────────────────────────────────────────

    def run_algorithm(self):
        if self.animation_running:
            messagebox.showinfo("Running",
                                "An animation is already running. Reset first.")
            return

        self.deadlocked_processes = []
        self.step_queue           = []
        self.log_box.delete(1.0, tk.END)

        try:
            n = int(self.process_entry.get())
            m = int(self.resource_entry.get())
            allocation = [[int(self.allocation_entries[i][j].get())
                           for j in range(m)] for i in range(n)]
            total = [int(self.total_entries[j].get()) for j in range(m)]
        except Exception:
            messagebox.showerror("Error", "Invalid or missing input values.")
            return

        available = []
        for j in range(m):
            used = sum(allocation[i][j] for i in range(n))
            av   = total[j] - used
            if av < 0:
                messagebox.showerror(
                    "Error",
                    f"Allocation for R{j} ({used}) exceeds total ({total[j]}).")
                return
            available.append(av)

        self._log(f"Initial Available: {available}\n\n", "info")
        self.animation_running = True

        if self.mode.get() == "banker":
            try:
                max_matrix = [[int(self.max_entries[i][j].get())
                               for j in range(m)] for i in range(n)]
            except Exception:
                messagebox.showerror("Error", "Invalid Max matrix values.")
                self.animation_running = False
                return

            # Validate need >= 0
            for i in range(n):
                for j in range(m):
                    if max_matrix[i][j] < allocation[i][j]:
                        messagebox.showerror(
                            "Error",
                            f"Max[P{i}][R{j}] < Allocation. Invalid.")
                        self.animation_running = False
                        return

            safe, seq, log = self.bankers_algorithm(
                allocation, max_matrix, available)

            for line in log:
                tag = "ok" if "can execute" in line else "muted"
                self._log(line + "\n", tag)

            self._show_stats(allocation, total, available,
                             "banker", safe=safe)

            if safe:
                self._log(f"\nSafe Sequence: {[f'P{p}' for p in seq]}\n",
                          "ok")
                self.draw_graph(allocation, finished=[])
                self.animate_execution(allocation, seq, available.copy(),
                                       mode="banker")
            else:
                self._log("\n⚠ System is in UNSAFE STATE — potential deadlock\n",
                          "err")
                self.draw_graph(allocation)
                self.animation_running = False

        else:
            try:
                request = [[int(self.request_entries[i][j].get())
                            for j in range(m)] for i in range(n)]
            except Exception:
                messagebox.showerror("Error", "Invalid Request matrix values.")
                self.animation_running = False
                return

            deadlocked, log = self.deadlock_detection(
                allocation, request, available)

            for line in log:
                tag = "ok" if "executed" in line else "muted"
                self._log(line + "\n", tag)

            self.deadlocked_processes = deadlocked
            self._show_stats(allocation, total, available,
                             "detection", deadlocked=deadlocked)

            if deadlocked:
                self._log(
                    f"\n⛔ Deadlock detected in processes: "
                    f"{[f'P{p}' for p in deadlocked]}\n", "err")
            else:
                self._log("\n✔ No deadlock — all processes can finish\n", "ok")

            self.draw_graph(allocation, request)
            executed = [i for i in range(n) if i not in deadlocked]
            if executed:
                self.animate_execution(allocation, executed,
                                       available.copy(), request,
                                       mode="detection")
            else:
                self.animation_running = False

    # ─────────────────────────────────────────
    #  ALGORITHMS
    # ─────────────────────────────────────────

    def bankers_algorithm(self, allocation, max_matrix, available):
        n = len(allocation)
        m = len(available)
        need = [[max_matrix[i][j] - allocation[i][j]
                 for j in range(m)] for i in range(n)]
        work     = available[:]
        finish   = [False] * n
        sequence = []
        log      = []
        log.append(f"Need Matrix:")
        for i in range(n):
            log.append(f"  P{i}: {need[i]}")
        log.append("")

        while len(sequence) < n:
            found = False
            for i in range(n):
                if (not finish[i]
                        and all(need[i][j] <= work[j] for j in range(m))):
                    for j in range(m):
                        work[j] += allocation[i][j]
                    finish[i] = True
                    sequence.append(i)
                    log.append(f"P{i} can execute → Work = {work}")
                    found = True
            if not found:
                break

        return len(sequence) == n, sequence, log

    def deadlock_detection(self, allocation, request, available):
        n    = len(allocation)
        m    = len(available)
        work = available[:]
        finish = [False] * n
        log    = [f"Initial Work: {work}", ""]

        while True:
            found = False
            for i in range(n):
                if (not finish[i]
                        and all(request[i][j] <= work[j] for j in range(m))):
                    for j in range(m):
                        work[j] += allocation[i][j]
                    finish[i] = True
                    log.append(f"P{i} executed → Work = {work}")
                    found = True
            if not found:
                break

        deadlocked = [i for i in range(n) if not finish[i]]
        return deadlocked, log


if __name__ == "__main__":
    root = tk.Tk()
    app  = DeadlockSimulator(root)
    root.mainloop()