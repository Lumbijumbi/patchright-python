# context_integration.py
# Example showing how to use fingerprint utilities to create a Playwright context.

from playwright.sync_api import sync_playwright
from patchright.fingerprint_utils import random_fp, load_fp_json, get_context_args

CAMOUFOX_PATH = """/usr/bin/camoufox"""

def main():
    # Example: use a random profile
    fp = random_fp()
    # Or load from a file: fp = load_fp_json("profiles/my_profile.json")

    context_args = get_context_args(fp, proxy=None)
    print("Context args:", context_args)

    with sync_playwright() as p:
        # Launch Chromium/Firefox depending on preference
        browser = p.firefox.launch(headless=False, executable_path=CAMOUFOX_PATH)
        context = browser.new_context(**context_args)
        page = context.new_page()
        page.goto("https://example.com")
        print("Page title:", page.title())
        context.close()
        browser.close()


if __name__ == "__main__":
    main()
