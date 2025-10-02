from django.shortcuts import render, get_object_or_404
from .models import League, Team

def league_list(request):
    """Show all leagues with navigation and the first league by default."""
    leagues = League.objects.all().order_by("external_id")
    current_league = leagues.first() if leagues.exists() else None
    teams = Team.objects.filter(league=current_league).order_by("-streak") if current_league else []

    return render(request, "tracker/leagues.html", {
        "leagues": leagues,
        "current_league": current_league,
        "teams": teams,
    })


def league_detail(request, league_id):
    """Show one league’s teams sorted by streak, with nav included."""
    leagues = League.objects.all().order_by("external_id")
    current_league = get_object_or_404(League, id=league_id)
    teams = Team.objects.filter(league=current_league).order_by("-streak")

    return render(request, "tracker/league_detail.html", {
        "leagues": leagues,
        "current_league": current_league,
        "teams": teams,
    })
