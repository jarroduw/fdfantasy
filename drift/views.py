from django.shortcuts import render
from django.views import View

# Create your views here.
from drift.models import *

class UserDashboardView:

    def get(self):
        """Need to return some general links"""

class LeagueView:

    def get(self):
        """Should show your league, if no league redirecto to join/create"""

    def post(self):
        """"Should save a new league with corresponding rules"""

class UserAccountView:

    def get(self):
        """Should show account view"""

    def post(self):
        """Should allow user to register and save a bunch of stuff"""

class UserTeamView:

    def get(self):
        """See full team and view scores for current week"""

    def post(self):
        """Create a new user team"""

class RacerView:

    def get(self):
        """See a given racer and their stats"""

class RaceTeamView:

    def get(self):
        """See a given team's racers"""

class ManufacturerTeamView:
    
    def get(self):
        """See a given manufacturer'r racers"""

class ListEventsView(View):

    ##TODO: Scraper is not getting right location and dates at least in post

    def get(self, request):
        """See a list of all events"""

        events = Event.objects.all()

        return render(request, 'drift/eventsList.html', {'events': events})

class EventView(View):

    def get(self, request, pk):
        """See a given event and any plans/results"""

        event = Event.objects.get(pk=pk)

        qualify = Qualify.objects.filter(event=pk).order_by('rank')

        races = Race.objects.filter(event=pk).order_by('-event_round')
        races2 = {
            '32': races.filter(event_round = 32),
            '16': races.filter(event_round = 16),
            '8': races.filter(event_round=8),
            '4': races.filter(event_round=4),
            '2': races.filter(event_round=2)
        }

        context = {'event': event, 'qualify': qualify, 'races': races2}
        
        return render(request, 'drift/event.html', context)

