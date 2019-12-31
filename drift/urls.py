from django.urls import path

from . import views
from . import api

app_name = 'drift'

urlpatterns = [
    path('api/event/', api.EventApi.as_view(), name='addEvent'),
    path('api/race/', api.RaceApi.as_view(), name='addRace'),
    path('api/racer/', api.RacerApi.as_view(), name='addRacer'),
    path('api/ranking/', api.RankingApi.as_view(), name='addRanking'),
    path('api/qualify/', api.QualifyApi.as_view(), name='addQualify'),
]