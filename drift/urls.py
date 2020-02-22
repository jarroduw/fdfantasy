from django.urls import path

from . import views
from . import api

app_name = 'drift'

urlpatterns = [
    path('', views.UserDashboardView.as_view(), name='home'),
    path('accounts/profile/', views.UserAccountView.as_view(), name='account'),
    path('accounts/register/', views.RegisterAccountView.as_view(), name='register'),
    path('accounts/register/<int:user_id>/', views.RegisterAccountView.as_view(), name='register'),
    path('accounts/changePassword/', views.ChangePasswordView.as_view(), name='changePassword'),
    path('activateEmail/<str:nonce>/', views.ActivateEmailView.as_view(), name='activateEmail'),
    path('events/', views.ListEventsView.as_view(), name='listEvents'),
    path('event/<int:pk>', views.EventView.as_view(), name='viewEvent'),
    path('teams/manufacturers/', views.ManufacturerTeamView.as_view(), name='listManufacturers'),
    path('teams/manufacturers/<str:teamName>/', views.ManufacturerTeamView.as_view(), name='showManufacturer'),
    path('teams/teams/', views.TeamView.as_view(), name='listTeams'),
    path('teams/teams/<str:teamName>/', views.TeamView.as_view(), name='showTeam'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('racers/', views.RacerListView.as_view(), name='listRacers'),
    path('racers/<int:pk>', views.RacerView.as_view(), name='viewRacer'),
    path('fantasyTeams', views.MyFantasyTeams.as_view(), name='myFantasyTeams'),
    path('fantasyTeams/teams/create/', views.CreateFantasyTeam.as_view(), name='createFantasyTeam'),
    path('fantasyTeams/teams/create/<int:league_id>/<str:key_code>/', views.CreateFantasyTeam.as_view(), name='createFantasyTeam'),
    path('fantasyTeams/teams/create/<str:league_id>/', views.CreateFantasyTeam.as_view(), name='createFantasyTeam'),
    path('fantasyTeams/teams/edit/<int:team_id>', views.CreateFantasyTeam.as_view(), name='editFantasyTeam'),
    path('fantasyTeams/teams/<int:team_id>', views.ViewFantasyTeam.as_view(), name='viewFantasyTeam'),
    path('fantasyTeams/teams/<int:team_id>/<int:event_id>', views.ViewFantasyTeam.as_view(), name='viewFantasyTeam'),
    path('leagues/', views.AllLeagues.as_view(), name='allLeagues'),
    path('leagues/<int:pk>/', views.LeagueView.as_view(), name='league'),
    path('leagues/create/', views.CreateLeagueView.as_view(), name='createLeague'),
    path('leagues/create/<int:league_id>/', views.CreateLeagueView.as_view(), name='createLeague'),
    path('leagues/invite/<int:league_id>/', views.InviteUsersToJoinLeague.as_view(), name='inviteToJoinLeague'),
    path('api/event/', api.EventApi.as_view(), name='addEvent'),
    path('api/race/', api.RaceApi.as_view(), name='addRace'),
    path('api/racer/', api.RacerApi.as_view(), name='addRacer'),
    path('api/ranking/', api.RankingApi.as_view(), name='addRanking'),
    path('api/qualify/', api.QualifyApi.as_view(), name='addQualify'),
    path('api/activate/', api.ActivateDriverApi.as_view(), name='activateDriver'),
    path('api/getPoints/<int:event>/<int:team>/<int:racer>', api.PointsApi.as_view(), name='points'),
]