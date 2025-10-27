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
    "platform": "Win32",
    "languages": ["en-US", "en"],
    "device_memory": 8,
    "hardware_concurrency": 8,
    "max_touch_points": 0,
    "color_depth": 24,
    "webdriver": False,
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
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    ]
    platforms = ["Win32", "MacIntel", "iPhone"]
    ua = random.choice(user_agents)
    
    # Match platform to user agent
    if "Windows" in ua:
        platform = "Win32"
    elif "Macintosh" in ua:
        platform = "MacIntel"
    elif "iPhone" in ua:
        platform = "iPhone"
    else:
        platform = random.choice(platforms)
    
    fp = {
        "user_agent": ua,
        "viewport": {"width": int(vw[0]), "height": int(vw[1])},
        "timezone": random.choice(["Europe/Berlin", "America/New_York", "Asia/Tokyo"]),
        "locale": random.choice(["en-US", "de-DE", "fr-FR"]),
        "platform": platform,
        "languages": random.choice([["en-US", "en"], ["de-DE", "de"], ["fr-FR", "fr"]]),
        "device_memory": random.choice([4, 8, 16]),
        "hardware_concurrency": random.choice([4, 8, 12, 16]),
        "max_touch_points": 0 if platform in ["Win32", "MacIntel"] else random.choice([5, 10]),
        "color_depth": 24,
        "webdriver": False,
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
    # New fields with defaults
    fp["platform"] = fp.get("platform") or DEFAULT_FP["platform"]
    fp["languages"] = fp.get("languages") or DEFAULT_FP["languages"]
    if not isinstance(fp["languages"], list):
        fp["languages"] = [fp["languages"]] if fp["languages"] else DEFAULT_FP["languages"]
    try:
        fp["device_memory"] = int(fp.get("device_memory", DEFAULT_FP["device_memory"]))
    except Exception:
        fp["device_memory"] = DEFAULT_FP["device_memory"]
    try:
        fp["hardware_concurrency"] = int(fp.get("hardware_concurrency", DEFAULT_FP["hardware_concurrency"]))
    except Exception:
        fp["hardware_concurrency"] = DEFAULT_FP["hardware_concurrency"]
    try:
        fp["max_touch_points"] = int(fp.get("max_touch_points", DEFAULT_FP["max_touch_points"]))
    except Exception:
        fp["max_touch_points"] = DEFAULT_FP["max_touch_points"]
    try:
        fp["color_depth"] = int(fp.get("color_depth", DEFAULT_FP["color_depth"]))
    except Exception:
        fp["color_depth"] = DEFAULT_FP["color_depth"]
    fp["webdriver"] = bool(fp.get("webdriver", DEFAULT_FP["webdriver"]))
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


def generate_js_overrides(fp: Dict[str, Any]) -> str:
    """Generate JavaScript code to override navigator and related properties.
    
    Returns a safe JavaScript string that can be passed to page.add_init_script()
    to spoof fingerprint properties before page scripts run.
    
    Args:
        fp: Fingerprint dictionary with spoofing parameters
        
    Returns:
        JavaScript code as a string
    """
    # Extract values with safe defaults
    platform = fp.get("platform", DEFAULT_FP["platform"])
    languages = fp.get("languages", DEFAULT_FP["languages"])
    device_memory = fp.get("device_memory", DEFAULT_FP["device_memory"])
    hardware_concurrency = fp.get("hardware_concurrency", DEFAULT_FP["hardware_concurrency"])
    max_touch_points = fp.get("max_touch_points", DEFAULT_FP["max_touch_points"])
    color_depth = fp.get("color_depth", DEFAULT_FP["color_depth"])
    webdriver = fp.get("webdriver", DEFAULT_FP["webdriver"])
    user_agent = fp.get("user_agent", DEFAULT_FP["user_agent"])
    viewport = _normalize_viewport(fp.get("viewport"))
    
    # Convert Python types to JS-safe values
    languages_js = json.dumps(languages)
    webdriver_js = "true" if webdriver else "false"
    
    js_code = f"""
// Fingerprint override script - injected before page load
(function() {{
    'use strict';
    
    // Override navigator properties
    try {{
        Object.defineProperty(navigator, 'platform', {{
            get: () => '{platform}'
        }});
    }} catch (e) {{}}
    
    try {{
        Object.defineProperty(navigator, 'languages', {{
            get: () => {languages_js}
        }});
    }} catch (e) {{}}
    
    try {{
        Object.defineProperty(navigator, 'language', {{
            get: () => {languages_js}[0]
        }});
    }} catch (e) {{}}
    
    try {{
        Object.defineProperty(navigator, 'deviceMemory', {{
            get: () => {device_memory}
        }});
    }} catch (e) {{}}
    
    try {{
        Object.defineProperty(navigator, 'hardwareConcurrency', {{
            get: () => {hardware_concurrency}
        }});
    }} catch (e) {{}}
    
    try {{
        Object.defineProperty(navigator, 'maxTouchPoints', {{
            get: () => {max_touch_points}
        }});
    }} catch (e) {{}}
    
    try {{
        Object.defineProperty(navigator, 'webdriver', {{
            get: () => {webdriver_js}
        }});
    }} catch (e) {{}}
    
    // Override screen properties
    try {{
        Object.defineProperty(screen, 'colorDepth', {{
            get: () => {color_depth}
        }});
    }} catch (e) {{}}
    
    try {{
        Object.defineProperty(screen, 'pixelDepth', {{
            get: () => {color_depth}
        }});
    }} catch (e) {{}}
    
    try {{
        Object.defineProperty(screen, 'width', {{
            get: () => {viewport["width"]}
        }});
    }} catch (e) {{}}
    
    try {{
        Object.defineProperty(screen, 'height', {{
            get: () => {viewport["height"]}
        }});
    }} catch (e) {{}}
    
    try {{
        Object.defineProperty(screen, 'availWidth', {{
            get: () => {viewport["width"]}
        }});
    }} catch (e) {{}}
    
    try {{
        Object.defineProperty(screen, 'availHeight', {{
            get: () => {viewport["height"]}
        }});
    }} catch (e) {{}}
    
    // Override userAgent if needed
    try {{
        Object.defineProperty(navigator, 'userAgent', {{
            get: () => '{user_agent}'
        }});
    }} catch (e) {{}}
    
}})();
"""
    return js_code
