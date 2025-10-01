import time
import re
import requests
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from tracker.models import Season, Team, Match
from playwright.sync_api import sync_playwright



API_FEED_FMT = (
    "https://vgls-vs001.akamaized.net/vfl/feeds/?/bet9javirtuals/en/"
    "Africa:Lagos/gismo/stats_season_lastx/{season_id}/13"
)
LEAGUE_MAP = {
    0: "English League",
    2: "German League",
    3: "Spanish League",
    4: "Italian League",
    5: "French League",
    7: "Portuguese League",
}


class Command(BaseCommand):
    help = "Run the long-running Bet9ja season tracker."

    def add_arguments(self, parser):
        parser.add_argument("--poll-interval", type=int, default=10, help="Polling seconds")

    def handle(self, *args, **options):
        poll_interval = options.get("poll_interval") or 10
        current_season_id = None

        while True:
            if not current_season_id:
                current_season_id = self.capture_new_season_id()
                if not current_season_id:
                    self.stdout.write("⚠️ Could not capture season ID, retrying...")
                    time.sleep(30)
                    continue

                season, created = Season.objects.get_or_create(season_id=str(current_season_id))
                if created:
                    season.started_at = datetime.utcnow()
                    season.active = True
                    season.save()
                    self.stdout.write(f"🏁 New season {season.season_id} created")

            # process range of 7
            # at the top of run_tracker.py
            RELEVANT_OFFSETS = [0, 2, 3, 4, 5, 7]

# inside handle()
            base_id = int(current_season_id)
            for offset in RELEVANT_OFFSETS:
                   sid = str(base_id + offset)
                   matches = self.fetch_all_matches(sid)
                   if matches:
                      new_count = self.process_matches_for_season(matches, sid)
                      if new_count:
                         self.stdout.write(f"✅ Processed {new_count} match(es) for {sid}")

            # check season end
            base_matches = self.fetch_all_matches(current_season_id)
            if base_matches and self.season_has_ended(base_matches):
                season.active = False
                season.ended_at = datetime.utcnow()
                season.save()
                self.stdout.write(f"🏁 Season {current_season_id} ended")
                current_season_id = None  # will capture again

            time.sleep(poll_interval)

    def capture_new_season_id(self):
        self.stdout.write("🎭 Launching Playwright to capture new season ID...")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)  # show browser to debug
            page = browser.new_page()
            page.goto("https://st-cdn001.akamaized.net/bet9javirtuals/en/1/category/1111")

            captured = []

            def log_request(req):
                if "stats_season_lastx" in req.url:
                    captured.append(req.url)

            page.on("request", log_request)

            try:
                page.wait_for_selector("a:has-text('Virtual Football English League')", timeout=15000)
                self.stdout.write("✅ Found league link, clicking...")
                page.click("a:has-text('Virtual Football English League')")
            except Exception:
                self.stdout.write("❌ Could not find English League link")

            page.wait_for_timeout(10000)  # wait 10s to capture
            browser.close()

        if captured:
            match = re.search(r"stats_season_lastx/(\d+)/", captured[0])
            if match:
                season_id = match.group(1)
                self.stdout.write(f"🎯 Captured season ID: {season_id}")
                return season_id

        self.stdout.write("⚠️ No season ID captured")
        return None


    def fetch_all_matches(self, season_id):
        url = API_FEED_FMT.format(season_id=season_id)
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            self.stdout.write(f"API error {season_id}: {e}")
            return None

        try:
            doc = data.get("doc", [None])[0]
            round_data = doc.get("data") if doc else []
            matches = []
            if isinstance(round_data, dict):
                matches = round_data.get("matches", []) or []
            elif isinstance(round_data, list):
                for rd in round_data:
                    if "matches" in rd:
                        matches.extend(rd["matches"])
            return matches
        except Exception as e:
            self.stdout.write(f"Parse error {season_id}: {e}")
            return None

    @transaction.atomic
    def process_matches_for_season(self, matches, season_id):
        new_count = 0
        season_obj, _ = Season.objects.get_or_create(season_id=str(season_id))
        sorted_matches = sorted(matches, key=lambda x: (x.get("round", 0), x.get("_id", 0)))

        for m in sorted_matches:
            mid = str(m.get("_id"))
            if Match.objects.filter(match_id=mid).exists():
                continue

            res = m.get("result", {})
            if res.get("home") is None or res.get("away") is None:
                continue

            home_name = m["teams"]["home"]["name"]
            away_name = m["teams"]["away"]["name"]
            hg, ag = int(res["home"]), int(res["away"])

        # 🔥 Try to extract league dynamically
            league_name = None
            if "competition" in m and isinstance(m["competition"], dict):
                league_name = m["competition"].get("name")
            elif "league" in m:
                league_name = m.get("league")
                
            if not league_name:
                sid = int(season_id)
                base_id = sid // 7 * 7
                offset = sid - base_id
                league_name = LEAGUE_MAP.get(offset, f"League {offset}")  # fallback if not found

            Match.objects.create(
                match_id=mid,
                season=season_obj,
                round_number=m.get("round", 0) or 0,
                home_team=home_name,
                away_team=away_name,
                home_score=hg,
                away_score=ag,
                league = league_name,
                processed=True,
            )

            home, _ = Team.objects.get_or_create(
                name=home_name,
                current_season=season_obj,
                defaults={"league": league_name, "streak": 0}
            )
            away, _ = Team.objects.get_or_create(
                name=away_name,
                current_season=season_obj,
                defaults={"league": league_name, "streak": 0}
            )
            # ✅ Always enforce correct league
            if not home.league or home.league != league_name:
               home.league = league_name
               home.save(update_fields=["league"])

            if not away.league or away.league != league_name:
               away.league = league_name
               away.save(update_fields=["league"])


            if hg == ag:
                home.draws += 1
                away.draws += 1
                home.streak = 0
                away.streak = 0
            else:
                if hg > ag:
                    home.wins += 1
                    away.losses += 1
                else:
                    away.wins += 1
                    home.losses += 1
                home.streak = (home.streak or 0) + 1
                away.streak = (away.streak or 0) + 1

            home.save()
            away.save()
            new_count += 1

        return new_count

    def season_has_ended(self, matches):
        rounds = [m.get("round", 0) for m in matches]
        if not rounds:
            return False
        max_round = max(rounds)
        if max_round < 30:
            return False
        last_round_matches = [m for m in matches if m.get("round", 0) == max_round]
        return all(m.get("result", {}).get("home") is not None and m.get("result", {}).get("away") is not None for m in last_round_matches)
