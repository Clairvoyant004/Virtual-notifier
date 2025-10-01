from django.db import models
from django.utils import timezone

class Season(models.Model):
    season_id = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"Season {self.season_id}"


class Team(models.Model):
    name = models.CharField(max_length=255)
    league = models.CharField(max_length=255, blank=True, null=True)
    current_season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="teams")
    streak = models.IntegerField(default=0)
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)
    draws = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    league = models.CharField(max_length=100, blank=True, null=True)  # ✅ NEW
    processed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("name", "current_season")

    def reset_streak(self):
        self.streak = 0
        self.save(update_fields=["streak", "last_updated"])

    def __str__(self):
        return f"{self.name} ({self.current_season.season_id})"


class Match(models.Model):
    match_id = models.CharField(max_length=128, unique=True)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="matches")
    round_number = models.IntegerField(default=0)
    home_team = models.CharField(max_length=255)
    away_team = models.CharField(max_length=255)
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    league = models.CharField(max_length=255, blank=True, null=True)  # 
    processed = models.BooleanField(default=False)
    fetched_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Match {self.match_id} r{self.round_number}"
