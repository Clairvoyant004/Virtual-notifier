from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import League, Team, Season

def league_list(request):
    """Show all leagues with navigation and the first league by default, only for active seasons."""
    all_leagues = League.objects.filter(
        team__current_season__active=True
    ).distinct().order_by("external_id")

    # Set the base page as the "current league"
    current_league = None

    teams = Team.objects.filter(
        league=current_league, current_season__active=True
    ).order_by("-streak") if current_league else []

    no_teams_message = "No teams yet" if current_league and not teams else None

    return render(request, "tracker/leagues.html", {
        "all_leagues": all_leagues,
        "current_league": current_league,
        "teams": teams,
        "no_teams_message": no_teams_message,
    })


def league_detail(request, league_id):
    """Show one league’s teams sorted by streak, only for active seasons."""
    all_leagues = League.objects.filter(
        team__current_season__active=True
    ).distinct().order_by("external_id")

    current_league = get_object_or_404(
        all_leagues, id=league_id
    )

    teams = Team.objects.filter(
        league=current_league, current_season__active=True
    ).order_by("-streak")

    no_teams_message = "No teams yet" if not teams else None

    return render(request, "tracker/leagues.html", {
        "all_leagues": all_leagues,
        "current_league": current_league,
        "teams": teams,
        "no_teams_message": no_teams_message,
    })
