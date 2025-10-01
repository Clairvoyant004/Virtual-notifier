from django.shortcuts import render
from tracker.models import Season, Team

def leagues_overview(request):
    season = Season.objects.filter(active=True).order_by("-started_at").first()
    league_tables = {}

    if season:
        teams = Team.objects.filter(current_season=season).exclude(league__isnull=True).exclude(league="")
        leagues = teams.values_list("league", flat=True).distinct()
        print("🔎 Leagues in DB:", list(leagues))
        # Group teams by league
        for league in teams.values_list("league", flat=True).distinct():
            league_teams = teams.filter(league=league).order_by("-streak", "-wins", "name")
            league_tables[league] = league_teams

    return render(request, "tracker/leagues.html", {
        "season": season,
        "league_tables": league_tables,
    })












'''from django.shortcuts import render, get_object_or_404
from tracker.models import Season, Team

def league_list(request):
    season = Season.objects.filter(active=True).order_by("-started_at").first()
    if not season:
        leagues = []
    else:
        leagues = (
            Team.objects.filter(current_season=season)
            .exclude(league__isnull=True)
            .exclude(league__exact="")
            .values_list("league", flat=True)
            .distinct()
            .order_by("league")
        )
    return render(request, "tracker/leagues_list.html", {"season": season, "leagues": leagues})


def league_detail(request, league_name):
    season = Season.objects.filter(active=True).order_by("-started_at").first()
    if not season:
        teams = []
    else:
        teams = (
            Team.objects.filter(current_season=season, league=league_name)
            .order_by("-streak", "-wins", "name")
        )
    return render(
        request,
        "tracker/league_detail.html",
        {"season": season, "league": league_name, "teams": teams},
    )
'''