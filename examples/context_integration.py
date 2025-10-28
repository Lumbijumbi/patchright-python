# context_integration.py
# Example showing how to use fingerprint utilities to create a Playwright context.

from playwright.sync_api import sync_playwright
from patchright.fingerprint_utils import random_fp, load_fp_json, get_context_args, generate_js_overrides

CAMOUFOX_PATH = """/usr/bin/camoufox"""

def main():
    # Example: use a random profile
    fp = random_fp()
    # Or load from a file: fp = load_fp_json("profiles/my_profile.json")

    print("Generated fingerprint:", fp)
    print()
    
    context_args = get_context_args(fp, proxy=None)
    print("Context args:", context_args)
    print()

    # Generate JS overrides for the fingerprint
    js_overrides = generate_js_overrides(fp)
    print("JS overrides generated (length:", len(js_overrides), "bytes)")
    print()

    with sync_playwright() as p:
        # Launch Chromium/Firefox depending on preference
        browser = p.firefox.launch(headless=False, executable_path=CAMOUFOX_PATH)
        context = browser.new_context(**context_args)
        
        # Add init script to inject fingerprint overrides before page load
        context.add_init_script(js_overrides)
        
        page = context.new_page()
        page.goto("https://example.com")
        print("Page title:", page.title())
        print()
        
        # Verify some overridden properties
        navigator_props = page.evaluate("""() => ({
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            languages: navigator.languages,
            deviceMemory: navigator.deviceMemory,
            hardwareConcurrency: navigator.hardwareConcurrency,
            maxTouchPoints: navigator.maxTouchPoints,
            webdriver: navigator.webdriver,
            colorDepth: screen.colorDepth,
            screenWidth: screen.width,
            screenHeight: screen.height
        })""")
        
        print("Injected navigator properties:")
        for key, value in navigator_props.items():
            print(f"  {key}: {value}")
        
        context.close()
        browser.close()


if __name__ == "__main__":
    main()
