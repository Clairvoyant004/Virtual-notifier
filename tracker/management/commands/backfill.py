from django.core.management.base import BaseCommand
from django.db.models import Q
from tracker.models import Team, Match

class Command(BaseCommand):
    help = "Backfill missing league names for teams using their matches"

    def handle(self, *args, **kwargs):
        updated = 0

        # Get all teams with no league
        teams = Team.objects.filter(Q(league__isnull=True) | Q(league=""))
        self.stdout.write(f"🔎 Found {teams.count()} teams without league...")

        for team in teams:
            # find a match where this team appeared in the same season
            match = Match.objects.filter(
                season=team.current_season
            ).filter(
                Q(home_team=team.name) | Q(away_team=team.name)
            ).exclude(league__isnull=True).exclude(league="").first()

            if match and match.league:
                team.league = match.league
                team.save(update_fields=["league"])
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Backfilled league for {updated} teams"))
