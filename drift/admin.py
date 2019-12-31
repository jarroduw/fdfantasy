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

admin.site.register(Event, EventAdmin)
admin.site.register(Racer, RacerAdmin)
admin.site.register(Ranking, RankingAdmin)
admin.site.register(Race, RaceAdmin)
admin.site.register(Qualify, QualifyAdmin)