from django.contrib import admin

from .models import *

# Register your models here.

class RaceAdmin(admin.ModelAdmin):
    list_display = ('event', 'event_round', 'top_seed', 'bottom_seed', 'winner')

class QualifyAdmin(admin.ModelAdmin):
    list_display = ('event', 'racer', 'rank')

class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'start', 'end')

class RacerAdmin(admin.ModelAdmin):
    list_display = ('name', 'team_name', 'car_number', 'car_manuf')

class RankingAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'racer', 'rank', 'points')

class ScoringValueAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'league', 'award', 'points')

class TeamAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'league', 'owner', 'name')

class LeagueAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'name', 'race_official')

class TeamActiveAdmin(admin.ModelAdmin):
    list_display = ('modified_at', 'status')

admin.site.register(Event, EventAdmin)
admin.site.register(Racer, RacerAdmin)
admin.site.register(Ranking, RankingAdmin)
admin.site.register(Race, RaceAdmin)
admin.site.register(Qualify, QualifyAdmin)
admin.site.register(ScoringValue, ScoringValueAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(League, LeagueAdmin)
admin.site.register(TeamActive, TeamActiveAdmin)
admin.site.register(DraftDate)
admin.site.register(DraftOrder)
admin.site.register(MatchupSeed)
admin.site.register(ScoringEvent)
admin.site.register(Notification)
admin.site.register(Season)
admin.site.register(WaiverWire)
admin.site.register(WaiverWireRemove)
admin.site.register(WaiverPriority)
