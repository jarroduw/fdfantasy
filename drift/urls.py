from django.urls import path

from . import views
from . import api

app_name = 'drift'

urlpatterns = [
    path('events/', views.ListEventsView.as_view(), name='listEvents'),
    path('event/<int:pk>', views.EventView.as_view(), name='viewEvent'),
    path('api/event/', api.EventApi.as_view(), name='addEvent'),
    path('api/race/', api.RaceApi.as_view(), name='addRace'),
    path('api/racer/', api.RacerApi.as_view(), name='addRacer'),
    path('api/ranking/', api.RankingApi.as_view(), name='addRanking'),
    path('api/qualify/', api.QualifyApi.as_view(), name='addQualify'),
]