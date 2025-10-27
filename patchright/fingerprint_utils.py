# fingerprint_utils.py
# Robust fingerprint utilities for Playwright context creation

import json
import random
from typing import Any, Dict, Tuple

# Default viewport list (width, height)
VIEWPORTS = [
    (1920, 1080), (1366, 768), (1280, 800), (1536, 864),
    (375, 812), (414, 896), (390, 844), (360, 800)
]

DEFAULT_FP = {
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "viewport": {"width": 1280, "height": 800},
    "timezone": "Europe/Berlin",
    "locale": "en-US",
}


def _normalize_viewport(viewport: Any) -> Dict[str, int]:
    """Normalize the viewport representation.

    Accepts tuple/list (w,h), dict {"width":.., "height":..}, or falsy.
    Returns a dict with integer width and height.
    """
    if isinstance(viewport, (list, tuple)) and len(viewport) >= 2:
        try:
            w = int(viewport[0])
            h = int(viewport[1])
            return {"width": w, "height": h}
        except Exception:
            pass
    if isinstance(viewport, dict):
        w = viewport.get("width")
        h = viewport.get("height")
        try:
            return {"width": int(w), "height": int(h)}
        except Exception:
            return {"width": int(DEFAULT_FP["viewport"]["width"]), "height": int(DEFAULT_FP["viewport"]["height"])}
    # fallback: pick random viewport
    vw = random.choice(VIEWPORTS)
    return {"width": int(vw[0]), "height": int(vw[1])}


def random_fp() -> Dict[str, Any]:
    """Generate a random, but sane fingerprint dict.

    The returned dict is safe to pass through get_context_args() to Playwright.
    """
    vw = random.choice(VIEWPORTS)
    fp = {
        "user_agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        ]),
        "viewport": {"width": int(vw[0]), "height": int(vw[1])},
        "timezone": random.choice(["Europe/Berlin", "America/New_York", "Asia/Tokyo"]),
        "locale": random.choice(["en-US", "de-DE", "fr-FR"]),
        # Optional additional fields
        "device_scale_factor": random.choice([1, 1.25, 1.5, 2]),
        "color_scheme": random.choice(["light", "dark"]),
    }
    return fp


def load_fp_json(path: str) -> Dict[str, Any]:
    """Load fingerprint JSON and normalize fields to safe types."""
    with open(path, "r", encoding="utf-8") as f:
        fp = json.load(f)
    # Ensure viewport
    fp["viewport"] = _normalize_viewport(fp.get("viewport"))
    # Ensure user_agent
    fp["user_agent"] = fp.get("user_agent") or DEFAULT_FP["user_agent"]
    # timezone/locale defaults
    fp["timezone"] = fp.get("timezone") or DEFAULT_FP["timezone"]
    fp["locale"] = fp.get("locale") or DEFAULT_FP["locale"]
    # device_scale_factor fallback
    try:
        fp["device_scale_factor"] = float(fp.get("device_scale_factor", 1))
    except Exception:
        fp["device_scale_factor"] = 1
    return fp


def get_context_args(fp: Dict[str, Any], proxy: str = None) -> Dict[str, Any]:
    """Return a dict of Playwright new_context keyword args built from fp.

    Guarantees viewport is {'width': int, 'height': int} and other sane defaults.
    """
    vp = _normalize_viewport(fp.get("viewport"))
    args = {
        "user_agent": fp.get("user_agent", DEFAULT_FP["user_agent"]),
        "viewport": vp,
        "locale": fp.get("locale", DEFAULT_FP["locale"]),
        "timezone_id": fp.get("timezone", DEFAULT_FP["timezone"]),
        "device_scale_factor": float(fp.get("device_scale_factor", 1)),
        "color_scheme": fp.get("color_scheme", "light"),
    }
    if proxy:
        # Accept proxy as "ip:port" or full URL like "http://user:pass@ip:port"
        args["proxy"] = {"server": proxy}
    return args
