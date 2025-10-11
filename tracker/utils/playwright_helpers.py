import re
import time
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError

def discover_season_id_via_playwright(
    base_url="https://st-cdn001.akamaized.net/bet9javirtuals/en/1/category/1111",
    headless=True,
    listen_seconds=10,
    max_retries=3,
    click_league_text="Virtual Football English League",
):
    """
    Fetch season_id from Bet9ja Virtuals using Playwright (headless-safe version).
    Works locally and in production (e.g. PythonAnywhere, Docker).
    """

    for attempt in range(1, max_retries + 1):
        print(f"🎭 Discovering new season ID (attempt {attempt}/{max_retries})...")

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=headless,
                    args=[
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                        "--disable-gpu",
                        "--disable-dev-shm-usage",
                        "--single-process",
                        "--disable-accelerated-2d-canvas",
                    ],
                )

                page = browser.new_page()
                captured = []

                def on_request(req):
                    url = req.url
                    if "stats_season_lastx" in url or "stats_season" in url:
                        captured.append(url)
                        print("📡 Captured:", url)

                page.on("request", on_request)

                print("🌍 Navigating to base page...")
                page.goto(base_url, wait_until="networkidle", timeout=60000)

                # Use Playwright's text selector (this works even for dynamic DOM)
                try:
                    print(f"🔍 Waiting for league link: {click_league_text}")
                    page.wait_for_selector(f"text={click_league_text}", timeout=20000)
                    print("✅ Clicking league link...")
                    page.click(f"text={click_league_text}")
                except PWTimeoutError:
                    print("⚠️ Could not find league link — continuing anyway.")

                print(f"🎧 Listening for {listen_seconds}s of network requests...")
                page.wait_for_timeout(listen_seconds * 1000)

                browser.close()

                for url in captured:
                    match = re.search(r"stats_season_lastx/(\d+)/", url) or re.search(r"stats_season/(\d+)", url)
                    if match:
                        season_id = match.group(1)
                        print("🎯 Found season ID:", season_id)
                        return season_id

                print(f"❌ No valid season ID captured in attempt {attempt}/{max_retries}")

        except Exception as e:
            print(f"⚠️ Playwright attempt {attempt} failed:", repr(e))

        time.sleep(3)

    print("🚫 Failed to capture season ID after all retries.")
    return None


if __name__ == "__main__":
    sid = discover_season_id_via_playwright(headless=False)
    print("✅ Season ID result:", sid)
