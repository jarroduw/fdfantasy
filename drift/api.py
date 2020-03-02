from django.db import transaction
from django.conf import settings
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import get_template

from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from .models import *
from .serializers import *

class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

class UserCheckin:
    permission_classes = [IsAuthenticated|ReadOnly]

    def get(self):
        """See all user checkins"""

    def post(self):
        """API call for user checkin"""

class ScoringValues:
    permission_classes = [IsAuthenticated|ReadOnly]

    def get(self):
        """Should return all scoring values for a given league"""

    def post(self):
        """Should save all scoring values for a given league"""

class ActivateRacer:
    permission_classes = [IsAuthenticated|ReadOnly]

    def post(self):
        """API Call to activate a single racer"""

class DeactivateRacer:
    permission_classes = [IsAuthenticated|ReadOnly]

    def post(self):
        """API Call to deactivate a single racer"""

###################################################################33
## To Do for ingest
class EventApi(APIView):
    permission_classes = [IsAuthenticated|ReadOnly]

    def post(self, request, format=None):
        """API call to create a new event"""
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
            )

    def get(self, request, format=None):
        """API call to get object based on features in json"""
        data = request.data
        result = Event.objects.filter(**data)
        serializer = EventSerializer(*result)
        return Response(serializer.data)

class QualifyApi(APIView):
    permission_classes = [IsAuthenticated|ReadOnly]
    def post(self, request, format=None):
        """API call to set the qualify rank"""

        serializer = QualifySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
            )

class RacerApi(APIView):
    permission_classes = [IsAuthenticated|ReadOnly]
    def post(self, request, format=None):
        """API call to store a racer."""

        serializer = RacerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
            )

    def get(self, request, format=None):
        """API call to get object based on features in json"""
        data = request.data
        result = Racer.objects.filter(**data)
        serializer = RacerSerializer(*result)
        return Response(serializer.data)

class RankingApi(APIView):
    permission_classes = [IsAuthenticated|ReadOnly]
    def post(self, request, format=None):
        serializer = RankingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
            )

class RaceApi(APIView):
    permission_classes = [IsAuthenticated|ReadOnly]
    def post(self, request, format=None):
        """API Call to store a race"""
        serializer = RaceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
            )

class ActivateDriverApi(APIView):
    permission_classes = [IsAuthenticated|ReadOnly]

    def post(self, request):
        serializer = TeamActiveSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PointsApi(APIView):
    permission_classes = [IsAuthenticated|ReadOnly]

    def get(self, request, event, team, racer):
        data = getPoints(event, team, racer)
        serializer = ScoringEventSerializer(data)
        return Response(serializer.data)

def getPoints(event, team, racer):
    data = ScoringEvent.objects.all(team=team, event=event, racer=racer)
    return data

def getAllPoints(team, racer):
    data = ScoringEvent.objects.all(team=team, racer=racer)
    return data

class NotificationApi(APIView):
    permission_classes = [IsAuthenticated|ReadOnly]

    def get(self, request):
        data = getNotifications(request.user)
        serializer = NotificationSerializer(data)
        return Response(serializer.data)

def getNotifications(user):
    notes = Notification.objects.filter(user=user)
    return notes

class CheckWaiverWire(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        self.checkWaiverWire()
        return Response({'msg': 'success'})

    def checkWaiverWire(self):
        waivers = WaiverWire.objects.filter(active=True).order_by('team__waiverpriority', 'team__id')
        waivers = [x for x in waivers if x.getExpired()==True or x.team.waiverpriority.firstInOrder()==True]
        while len(waivers) > 0:
            waiver = waivers[0]
            with transaction.atomic():
                addRacerToTeam(waiver.team, waiver.racer, waiver=waiver)
                for removeRacer in waiver.waiverwireremove_set.filter(active=True):
                    waiver.team.racers.remove(removeRacer.racer)
                    removeRacer.active = False
                    removeRacer.save()
            waivers = WaiverWire.objects.filter(active=True).order_by('team__waiverpriority', 'team__id')
            waivers = [x for x in waivers if x.getExpired()==True or x.team.waiverpriority.firstInOrder()==True]

def addRacerToWaiver(team, racer, waiver=None):
    skipWaiver = False
    try:
        existing = team.waiverwire_set.filter(active=True, racer=racer)
        if len(existing) > 0:
            skipWaiver = True
            ww = None
    except ObjectDoesNotExist:
        pass
    if not skipWaiver:
        ww = WaiverWire.objects.create(
            team=team,
            racer=racer
        )
        ww.save()
        email_msg = get_template(
            'drift/email_driverAddedToWaiver.html'
            ).render({
                'racer': racer,
                'team': team,
                })
        send_mail(
            "Player Added to Waiver Wire",
            email_msg,
            settings.DEFAULT_FROM_EMAIL,
            [team.owner.email]
            )
        note = Notification.objects.create(
            user=team.owner,
            msg='You added %s to the waiver wire!' % (racer.name,)
        )
        note.save()
    return ww

def addRacerToTeam(team, racer):
    teamsInLeague = [team.id for team in team.league.team_set.all()]
    team.racers.add(racer)
    team.save()
    waiver = team.waiverwire_set.filter(racer=racer, active=True)
    ##Should only be one
    for w in waiver:
        w.active=False
        w.save()
    team.waiverpriority.setOrderToMax()
    email_msg = get_template(
        'drift/email_driverAdded.html'
        ).render({'racer': racer})
    send_mail(
        "Player Added to Team",
        email_msg,
        settings.DEFAULT_FROM_EMAIL,
        [team.owner.email]
        )
    note = Notification.objects.create(
        user=team.owner,
        msg='You added %s to your team!' % (racer.name,)
    )
    note.save()