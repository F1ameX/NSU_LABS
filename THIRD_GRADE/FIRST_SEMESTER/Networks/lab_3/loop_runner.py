import os
import re
import html
import asyncio
from typing import List, Tuple, Dict, Any

import aiohttp
from dotenv import load_dotenv

from gui import App
from loop_runner import AsyncioLoopThread

load_dotenv()

GRAPHOPPER_API_KEY = os.getenv("GRAPHOPPER_API_KEY", "").strip()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "").strip()
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "").strip()
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "").strip()

_TAG_RE = re.compile(r"<[^>]+>")


def _clean_html(text: str) -> str:
    if not text:
        return ""
    text = html.unescape(text)
    text = _TAG_RE.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _best_description(detail: Dict[str, Any]) -> str:
    w = detail.get("wikipedia_extracts")
    if isinstance(w, dict):
        t = _clean_html(w.get("text", ""))
        if t:
            return t
    info = detail.get("info")
    if isinstance(info, dict):
        t = _clean_html(info.get("descr", ""))
        if t:
            return t
    return ""


# ------------------ HTTP корутины ------------------

async def search_locations(query: str) -> List[Tuple[str, float, float]]:
    """GraphHopper geocode → [(name, lat, lon), ...] до 5 штук."""
    if not query:
        return []

    url = "https://graphhopper.com/api/1/geocode"
    params = {
        "q": query,
        "limit": 5,
        "key": GRAPHOPPER_API_KEY,
        # "locale": "ru",  # при желании можно включить локаль
    }
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()

    hits = data.get("hits", []) or []
    out: List[Tuple[str, float, float]] = []
    for h in hits[:5]:
        name = h.get("name") or ""
        point = h.get("point") or {}
        lat = point.get("lat")
        lon = point.get("lng")
        if name and isinstance(lat, (float, int)) and isinstance(lon, (float, int)):
            out.append((name, float(lat), float(lon)))
    return out


async def get_weather(lat: float, lon: float) -> Dict[str, Any]:
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
        "lang": "ru",
    }
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, params=params) as resp:
            resp.raise_for_status()
            return await resp.json()


async def get_places(lat: float, lon: float, radius_m: int = 1500, limit: int = 5) -> List[Dict[str, Any]]:
    """OpenTripMap через RapidAPI → список {'xid', 'name'}."""
    base = f"https://{RAPIDAPI_HOST}"
    url = f"{base}/en/places/radius"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST,
        "Accept": "application/json",
        "Accept-Language": "ru",
    }
    params = {"lat": lat, "lon": lon, "radius": radius_m, "limit": limit}
    timeout = aiohttp.ClientTimeout(total=20)
    async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
        async with session.get(url, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()

    features = data.get("features", []) or []
    pois: List[Dict[str, Any]] = []
    for ft in features:
        props = (ft or {}).get("properties", {}) or {}
        xid = props.get("xid")
        name = props.get("name") or ""
        if xid:
            pois.append({"xid": xid, "name": name})
    return pois


async def get_place_details(xid: str) -> Dict[str, Any]:
    base = f"https://{RAPIDAPI_HOST}"
    url = f"{base}/en/places/xid/{xid}"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST,
        "Accept": "application/json",
        "Accept-Language": "ru",
    }
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
        async with session.get(url) as resp:
            resp.raise_for_status()
            return await resp.json()


async def fetch_details(lat: float, lon: float, radius_m: int = 1500, limit: int = 5) -> Dict[str, Any]:
    """Параллель: погода + места; затем цепочка деталей по xid."""
    weather_task = asyncio.create_task(get_weather(lat, lon))
    places_task = asyncio.create_task(get_places(lat, lon, radius_m=radius_m, limit=limit))

    # мягче относимся к сбоям одного из независимых вызовов
    weather, places = await asyncio.gather(
        weather_task,
        places_task,
        return_exceptions=True,
    )
    if isinstance(weather, Exception):
        weather = {}
    if isinstance(places, Exception):
        places = []

    detail_tasks = [asyncio.create_task(get_place_details(p["xid"])) for p in places]
    details: List[Dict[str, Any]] = []
    if detail_tasks:
        results = await asyncio.gather(*detail_tasks, return_exceptions=True)
        for item, base in zip(results, places):
            if isinstance(item, Exception):
                details.append({"name": base.get("name", "") or "Без названия", "error": str(item)})
            else:
                if not item.get("name"):
                    item["name"] = base.get("name", "") or "Без названия"
                details.append(item)

    return {"weather": weather, "places": details}


# ------------------ Bootstrap ------------------

def main():
    has_geocode_key = bool(GRAPHOPPER_API_KEY)
    has_weather_and_places_keys = bool(OPENWEATHER_API_KEY and RAPIDAPI_KEY and RAPIDAPI_HOST)

    loop_thread = AsyncioLoopThread()
    loop_thread.start()

    app = App(
        loop_thread,
        search_locations_coro_factory=search_locations,
        fetch_details_coro_factory=lambda lat, lon: fetch_details(lat, lon, radius_m=1500, limit=5),
        best_description=_best_description,
        has_geocode_key=has_geocode_key,
        has_weather_and_places_keys=has_weather_and_places_keys,
    )

    try:
        app.mainloop()
    finally:
        loop_thread.shutdown(timeout=2.0)


if __name__ == "__main__":
    main()