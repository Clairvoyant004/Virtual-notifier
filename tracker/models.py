from django.db import models
from django.utils import timezone

class League(models.Model):
    name = models.CharField(max_length=255)
    external_id = models.BigIntegerField(unique=True)  # season id or competition id

    def __str__(self):
        return self.name

    def clean_up_inactive(self):
        """Mark the league as inactive if it has no active teams or seasons."""
        if not self.team_set.filter(current_season__active=True).exists():
            self.delete()  # Delete the league if no active teams or seasons exist


class Season(models.Model):
    season_id = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"Season {self.season_id}"

    def mark_as_inactive(self):
        """Mark the season as inactive."""
        self.active = False
        self.ended_at = timezone.now()
        self.save()


class Team(models.Model):
    name = models.CharField(max_length=100)
    current_season = models.ForeignKey(Season, on_delete=models.CASCADE)
    league = models.ForeignKey(League, on_delete=models.CASCADE, null=True, blank=True)
    streak = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)

    class Meta:
        unique_together = ("name", "current_season")

    def __str__(self):
        return f"{self.name} ({self.league})"


class Match(models.Model):
    match_id = models.CharField(max_length=128, unique=True)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="matches")
    round_number = models.IntegerField(default=0)
    home_team = models.CharField(max_length=255)
    away_team = models.CharField(max_length=255)
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    league = models.CharField(max_length=255, blank=True, null=True)
    processed = models.BooleanField(default=False)
    fetched_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Match {self.match_id} r{self.round_number}"
