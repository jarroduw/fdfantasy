from django.shortcuts import render

# Create your views here.
from drift.models import *

class UserDashboard:

    def get(self):
        """Need to return some general links"""

class League:

    def get(self):
        """Should show your league, if no league redirecto to join/create"""

    def post(self):
        """"Should save a new league with corresponding rules"""


class User:

    def get(self):
        """Should show account view"""

    def post(self):
        """Should allow user to register and save a bunch of stuff"""

class Team:

    def get(self):
        """See full team and view scores for current week"""

class Racer:

    def get(self):
        """See a given racer and their stats"""

    def post(self):
        """Add/update a racer"""

class Event:

    def get(self):
        """See a given event and any plans/results"""

    def post(self):
        """Add an event"""

