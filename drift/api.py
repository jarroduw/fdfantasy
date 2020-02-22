from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status

from .models import *
from .serializers import *

class UserCheckin:

    def get(self):
        """See all user checkins"""

    def post(self):
        """API call for user checkin"""

class ScoringValues:

    def get(self):
        """Should return all scoring values for a given league"""

    def post(self):
        """Should save all scoring values for a given league"""

class ActivateRacer:

    def post(self):
        """API Call to activate a single racer"""

class DeactivateRacer:

    def post(self):
        """API Call to deactivate a single racer"""

###################################################################33
## To Do for ingest
class EventApi(APIView):

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

    def post(self, request):
        serializer = TeamActive(data=request.data)
        print(request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PointsApi(APIView):

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

    def get(self, request):
        data = getNotifications(request.user)
        serializer = NotificationSerializer(data)
        return Response(serializer.data)

def getNotifications(user):
    notes = Notification.objects.filter(user=user)
    return notes