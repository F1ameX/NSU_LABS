from __future__ import annotations
from typing import Callable, Awaitable, List, Tuple, Dict, Any
import tkinter as tk
from tkinter import messagebox


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
        self.geometry("860x640")

        self.loop_thread = loop_thread
        self.search_locations_coro_factory = search_locations_coro_factory
        self.fetch_details_coro_factory = fetch_details_coro_factory
        self.best_description = best_description
        self.has_geocode_key = has_geocode_key
        self.has_weather_and_places_keys = has_weather_and_places_keys

        self.locations: List[Tuple[str, float, float]] = []

        top = tk.Frame(self)
        top.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(top, text="Введите место:").pack(side=tk.LEFT)
        self.query_entry = tk.Entry(top, width=40)
        self.query_entry.pack(side=tk.LEFT, padx=8)
        self.search_btn = tk.Button(top, text="Искать (топ-5)", command=self.on_search_clicked)
        self.search_btn.pack(side=tk.LEFT)

        mid = tk.Frame(self)
        mid.pack(fill=tk.BOTH, expand=False, padx=10)

        tk.Label(mid, text="Найденные локации (выберите одну):").pack(anchor="w")
        self.listbox = tk.Listbox(mid, height=6)
        self.listbox.pack(fill=tk.X, pady=5)
        self.listbox.bind("<<ListboxSelect>>", self.on_location_selected)

        sep = tk.Frame(self, height=2, bg="#ddd")
        sep.pack(fill=tk.X, padx=10, pady=10)

        weather_frame = tk.Frame(self)
        weather_frame.pack(fill=tk.X, padx=10)
        tk.Label(weather_frame, text="Погода:", font=("Arial", 12, "bold")).pack(anchor="w")
        self.weather_label = tk.Label(weather_frame, text="—", justify="left")
        self.weather_label.pack(anchor="w", pady=(4, 0))

        places_frame = tk.Frame(self)
        places_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 10))
        tk.Label(places_frame, text="Интересные места:", font=("Arial", 12, "bold")).pack(anchor="w")
        self.places_text = tk.Text(places_frame, wrap="word")
        self.places_text.pack(fill=tk.BOTH, expand=True, pady=(4, 0))
        self.places_text.configure(state="disabled")

        self.status = tk.Label(self, text="Готово.", anchor="w")
        self.status.pack(fill=tk.X, side=tk.BOTTOM)

    def set_status(self, text: str):
        self.status.config(text=text)
        self.update_idletasks()

    def clear_results(self):
        self.weather_label.config(text="—")
        self.places_text.configure(state="normal")
        self.places_text.delete("1.0", tk.END)
        self.places_text.insert(tk.END, "—")
        self.places_text.configure(state="disabled")

    def on_search_clicked(self):
        query = self.query_entry.get().strip()
        if not query:
            messagebox.showinfo("Поиск", "Введите название места.")
            return
        if not self.has_geocode_key:
            messagebox.showerror("Ошибка", "GRAPHOPPER_API_KEY не задан.")
            return

        self.set_status("Ищу локации...")
        self.listbox.delete(0, tk.END)
        self.clear_results()

        coro = self._handle_search(query)
        _ = self.loop_thread.submit(coro)

    async def _handle_search(self, query: str):
        try:
            locations = await self.search_locations_coro_factory(query)
        except Exception as e:
            self.after(0, lambda err=e: self._on_search_error(err))
            return
        self.after(0, lambda: self._populate_locations(locations))

    def _on_search_error(self, e: Exception):
        self.set_status("Ошибка при поиске.")
        messagebox.showerror("Поиск", f"Не удалось выполнить поиск: {e}")

    def _populate_locations(self, locations: List[Tuple[str, float, float]]):
        self.locations = locations
        self.listbox.delete(0, tk.END)
        if not locations:
            self.listbox.insert(tk.END, "Ничего не найдено.")
            self.set_status("Готово.")
            return
        for name, lat, lon in locations:
            self.listbox.insert(tk.END, f"{name}  (lat={lat:.5f}, lon={lon:.5f})")
        self.set_status("Выберите локацию из списка.")

    def on_location_selected(self, _event):
        if not self.locations:
            return
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx >= len(self.locations):
            return

        name, lat, lon = self.locations[idx]

        self.set_status(f"Загружаю данные для: {name} ...")
        self.weather_label.config(text="Загрузка...")
        self.places_text.configure(state="normal")
        self.places_text.delete("1.0", tk.END)
        self.places_text.insert(tk.END, "Загрузка интересных мест...")
        self.places_text.configure(state="disabled")

        coro = self._handle_details(name, lat, lon)
        _ = self.loop_thread.submit(coro)

    async def _handle_details(self, name: str, lat: float, lon: float):
        try:
            result = await self.fetch_details_coro_factory(lat, lon)
        except Exception as e:
            self.after(0, lambda err=e: self._on_details_error(err))
            return
        self.after(0, lambda: self._populate_details(name, result))

    def _on_details_error(self, e: Exception):
        self.set_status("Ошибка при получении данных.")
        messagebox.showerror("Детали", f"Не удалось получить данные: {e}")

    def _populate_details(self, place_name: str, result: Dict[str, Any]):
        w = result.get("weather", {}) or {}
        temp = None
        desc = None
        if isinstance(w, dict):
            main = w.get("main") or {}
            temp = main.get("temp")
            we = w.get("weather") or []
            if we and isinstance(we, list) and isinstance(we[0], dict):
                desc = we[0].get("description")
        weather_text = f"Погода в {place_name}: "
        if temp is not None:
            weather_text += f"{temp:.1f}°C"
            if desc:
                weather_text += f", {desc}"
        else:
            weather_text += "нет данных"
        self.weather_label.config(text=weather_text)


        places = result.get("places", []) or []
        self.places_text.configure(state="normal")
        self.places_text.delete("1.0", tk.END)

        pretty: List[Tuple[str, str]] = []
        for d in places:
            nm = (d.get("name") or "").strip()
            if not nm:
                continue
            descr = self.best_description(d)
            if not descr:
                continue
            if len(descr) > 800:
                descr = descr[:800].rstrip() + "…"
            pretty.append((nm, descr))

        if not pretty:
            self.places_text.insert(tk.END, "Подходящие места с описанием не найдены в радиусе 1.5 км.")
        else:
            for i, (nm, ds) in enumerate(pretty, 1):
                self.places_text.insert(tk.END, f"{i}. {nm}\n")
                self.places_text.insert(tk.END, f"   {ds}\n\n")

        self.places_text.configure(state="disabled")
        self.set_status("Готово.")