from __future__ import annotations
from typing import Callable, Awaitable, List, Tuple, Dict, Any
import tkinter as tk
from tkinter import messagebox, ttk


class App(tk.Tk):
    def __init__(
        self,
        loop_thread,
        *,
        search_locations_coro_factory: Callable[[str], Awaitable[List[Tuple[str, float, float]]]],
        fetch_details_coro_factory: Callable[[float, float], Awaitable[Dict[str, Any]]],
        best_description: Callable[[Dict[str, Any]], str],
        has_geocode_key: bool,
        has_weather_and_places_keys: bool,
    ):
        super().__init__()
        self.title("Поиск мест • Погода • Интересные места (Async)")
        self.geometry("980x680")
        self.minsize(880, 580)

        self.loop_thread = loop_thread
        self.search_locations_coro_factory = search_locations_coro_factory
        self.fetch_details_coro_factory = fetch_details_coro_factory
        self.best_description = best_description
        self.has_geocode_key = has_geocode_key
        self.has_weather_and_places_keys = has_weather_and_places_keys
        self.locations: List[Tuple[str, float, float]] = []

        self._init_theme()   # только тёмная тема
        self._init_styles()

        root = ttk.Frame(self, padding=(10, 10, 10, 6), style="Root.TFrame")
        root.pack(fill=tk.BOTH, expand=True)

        # === SEARCH BAR (без лейбла и без плейсхолдера) ===
        search_card = ttk.Frame(root, style="Card.TFrame", padding=(10, 10))
        search_card.pack(fill=tk.X, pady=(0, 8))
        row = ttk.Frame(search_card, style="Card.TFrame")
        row.pack(fill=tk.X)
        self.query_entry = ttk.Entry(row, width=40, style="Input.TEntry")
        self.query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.search_btn = ttk.Button(row, text="Искать", style="Primary.TButton", command=self.on_search_clicked)
        self.search_btn.pack(side=tk.LEFT)

        # === PANED WINDOW ===
        pw = ttk.Panedwindow(root, orient=tk.HORIZONTAL)
        pw.pack(fill=tk.BOTH, expand=True, pady=(6, 6))
        pw.configure(style="Root.TFrame")

        left = ttk.Frame(pw, style="Card.TFrame", padding=(10, 10))
        right = ttk.Frame(pw)
        pw.add(left, weight=1)
        pw.add(right, weight=1)

        # — ограничение минимальной ширины панелей
        self._paned = pw
        self._pane_min = 360
        self._left = left
        self._right = right
        self._bind_paned_clamp()

        # === LEFT: LOCATIONS ===
        ttk.Label(left, text="Результаты поиска", style="Section.TLabel").pack(anchor="w")
        tree_container = ttk.Frame(left, style="Card.TFrame")
        tree_container.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

        columns = ("name", "lat", "lon")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=6, style="Modern.Treeview")
        self.tree.heading("name", text="Локация")
        self.tree.heading("lat", text="Широта")
        self.tree.heading("lon", text="Долгота")
        self.tree.column("name", width=360, anchor="w")
        self.tree.column("lat", width=80, anchor="center")
        self.tree.column("lon", width=80, anchor="center")

        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.LEFT, fill=tk.Y, padx=(6, 0))

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # === RIGHT: WEATHER + PLACES ===
        weather_card = ttk.Frame(right, style="Card.TFrame", padding=(10, 10))
        weather_card.pack(fill=tk.X)
        ttk.Label(weather_card, text="Погода", style="Section.TLabel").pack(anchor="w")
        self.weather_label = ttk.Label(weather_card, text="—", style="Body.TLabel", wraplength=420, justify="left")
        self.weather_label.pack(anchor="w", pady=(6, 0))

        places_card = ttk.Frame(right, style="Card.TFrame", padding=(10, 10))
        places_card.pack(fill=tk.BOTH, expand=True, pady=(6, 0))
        ttk.Label(places_card, text="Интересные места", style="Section.TLabel").pack(anchor="w")

        text_holder = ttk.Frame(places_card, style="Card.TFrame")
        text_holder.pack(fill=tk.BOTH, expand=True, pady=(6, 0))
        self.places_text = tk.Text(
            text_holder,
            wrap="word",
            relief="flat",
            padx=6,
            pady=6,
            bg=self._c("surface"),
            fg=self._c("text"),
            insertbackground=self._c("text"),
        )
        scroll = ttk.Scrollbar(text_holder, orient="vertical", command=self.places_text.yview)
        self.places_text.configure(yscrollcommand=scroll.set, state="disabled")
        self.places_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.LEFT, fill=tk.Y, padx=(6, 0))

        # === STATUS BAR ===
        status_bar = ttk.Frame(root, style="Status.TFrame")
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=(4, 0))
        self.status = ttk.Label(status_bar, text="Готово.", anchor="w", style="Status.TLabel")
        self.status.pack(fill=tk.X, padx=6, pady=4)

    # === PANED LIMITER ===
    def _bind_paned_clamp(self):
        self._paned.bind("<Configure>", self._on_paned_configure)

    def _on_paned_configure(self, _evt=None):
        """Держим панели не уже self._pane_min."""
        try:
            total = max(self._paned.winfo_width(), 1)
            minw = self._pane_min
            pos = self._paned.sashpos(0)
            lo = minw
            hi = max(total - minw, lo)
            if pos < lo:
                self._paned.sashpos(0, lo)
            elif pos > hi:
                self._paned.sashpos(0, hi)
        except Exception:
            pass

    # === THEME (только dark) ===
    def _init_theme(self):
        self._colors = {
            "bg": "#121416",
            "surface": "#1a1d20",
            "card": "#1f2327",
            "border": "#2a2f35",
            "text": "#e9eef3",
            "muted": "#a7b0b8",
            "brand": "#4aa7ff",
            "brand_hover": "#3a90e0",
            "ok": "#22c55e",
            "fail": "#ef4444",
            "status": "#0f1113",
        }
        self.configure(bg=self._c("bg"))

    def _c(self, name: str) -> str:
        return self._colors[name]

    def _init_styles(self):
        s = ttk.Style(self)
        try:
            s.theme_use("clam")
        except:
            pass
        s.configure("Root.TFrame", background=self._c("bg"))
        s.configure("Card.TFrame", background=self._c("card"), borderwidth=1, relief="solid")
        s.configure("Status.TFrame", background=self._c("status"))
        s.configure("Section.TLabel", font=("Segoe UI", 11, "bold"), foreground=self._c("text"), background=self._c("card"))
        s.configure("Body.TLabel", font=("Segoe UI", 10), foreground=self._c("text"), background=self._c("card"))
        s.configure("Status.TLabel", font=("Segoe UI", 9), foreground=self._c("muted"), background=self._c("status"))
        s.configure("Primary.TButton", background=self._c("brand"), foreground="white",
                    font=("Segoe UI", 10, "bold"), padding=(10, 4), borderwidth=0)
        s.map("Primary.TButton", background=[("active", self._c("brand_hover"))])
        s.configure("Input.TEntry", fieldbackground=self._c("surface"), foreground=self._c("text"), padding=6)
        s.configure("Modern.Treeview", background=self._c("card"), fieldbackground=self._c("card"),
                    foreground=self._c("text"), bordercolor=self._c("border"), rowheight=26)
        s.configure("Modern.Treeview.Heading", background=self._c("card"), foreground=self._c("muted"),
                    font=("Segoe UI", 9, "bold"), relief="flat")

    # === HELPERS ===
    def set_status(self, text: str):
        self.status.config(text=text)
        self.update_idletasks()

    def clear_results(self):
        self.weather_label.config(text="—")
        self.places_text.configure(state="normal")
        self.places_text.delete("1.0", tk.END)
        self.places_text.insert(tk.END, "—")
        self.places_text.configure(state="disabled")
        for i in self.tree.get_children():
            self.tree.delete(i)

    # === LOGIC ===
    def on_search_clicked(self):
        q = self.query_entry.get().strip()
        if not q:
            messagebox.showinfo("Поиск", "Введите название места.")
            return
        if not self.has_geocode_key:
            messagebox.showerror("Ошибка", "GRAPHOPPER_API_KEY не задан.")
            return
        self.set_status("Ищу локации…")
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.clear_results()
        _ = self.loop_thread.submit(self._handle_search(q))

    async def _handle_search(self, query: str):
        try:
            locs = await self.search_locations_coro_factory(query)
        except Exception as e:
            self.after(0, lambda err=e: self._on_search_error(err))
            return
        self.after(0, lambda: self._populate_locations(locs))

    def _on_search_error(self, e: Exception):
        self.set_status("Ошибка при поиске.")
        messagebox.showerror("Поиск", f"{e}")

    def _populate_locations(self, locs: List[Tuple[str, float, float]]):
        self.locations = locs
        [self.tree.delete(i) for i in self.tree.get_children()]
        if not locs:
            self.set_status("Ничего не найдено.")
            self.tree.insert("", "end", values=("—", "—", "—"))
            return
        for name, lat, lon in locs:
            self.tree.insert("", "end", values=(name, f"{lat:.5f}", f"{lon:.5f}"))
        self.set_status("Выберите локацию.")

    def _on_tree_select(self, _event=None):
        if not self.locations:
            return
        sel = self.tree.selection()
        if not sel:
            return
        idx = self.tree.index(sel[0])
        if idx >= len(self.locations):
            return
        name, lat, lon = self.locations[idx]
        self._select_location(name, lat, lon)

    def _select_location(self, name: str, lat: float, lon: float):
        self.set_status(f"Загружаю данные для: {name}…")
        self.weather_label.config(text="Загрузка…")
        self.places_text.configure(state="normal")
        self.places_text.delete("1.0", tk.END)
        self.places_text.insert(tk.END, "Загрузка интересных мест…")
        self.places_text.configure(state="disabled")
        _ = self.loop_thread.submit(self._handle_details(name, lat, lon))

    async def _handle_details(self, name: str, lat: float, lon: float):
        try:
            result = await self.fetch_details_coro_factory(lat, lon)
        except Exception as e:
            self.after(0, lambda err=e: self._on_details_error(err))
            return
        self.after(0, lambda: self._populate_details(name, result))

    def _on_details_error(self, e: Exception):
        self.set_status("Ошибка при получении.")
        messagebox.showerror("Детали", f"{e}")

    def _populate_details(self, place_name: str, result: Dict[str, Any]):
        w = result.get("weather", {}) or {}
        temp = w.get("main", {}).get("temp")
        desc = None
        we = w.get("weather") or []
        if we and isinstance(we, list) and we[0].get("description"):
            desc = we[0]["description"]
        weather_text = f"Погода в {place_name}: {temp:.1f}°C, {desc}" if temp is not None else f"Погода в {place_name}: нет данных"
        self.weather_label.config(text=weather_text)

        places = result.get("places", []) or []
        self.places_text.configure(state="normal")
        self.places_text.delete("1.0", tk.END)
        if not places:
            self.places_text.insert(tk.END, "Места не найдены.")
            self.places_text.configure(state="disabled")
            return
        for i, d in enumerate(places, 1):
            nm = (d.get("name") or "").strip()
            ds = self.best_description(d)
            if not nm or not ds:
                continue
            if len(ds) > 1000:
                ds = ds[:1000] + "…"
            self.places_text.insert(tk.END, f"{i}. {nm}\n   {ds}\n\n")
        self.places_text.configure(state="disabled")
        self.set_status("Готово.")