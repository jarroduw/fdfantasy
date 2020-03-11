from drift.models import *
from drift.permissions import *
from rest_framework import serializers

class LeagueSerializer(serializers.ModelSerializer):
    class Meta:
        model=League
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        exclude = ['created_at', 'modified_at']

class RacerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Racer
        exclude = ['created_at', 'modified_at']

class RankingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ranking
        exclude = ['created_at', 'modified_at']

class RaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Race
        exclude =  ['created_at', 'modified_at']

class QualifySerializer(serializers.ModelSerializer):
    class Meta:
        model = Qualify
        exclude = ['created_at', 'modified_at']

class TeamActiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamActive
        exclude = ['modified_at']
        permission_classes = [IsTeamOwner]

class ScoringEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoringEvent
        exclude = ['created_at', 'modified_at']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        
class DraftQueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = DraftQueue
        fields = '__all__'

class DraftPickSerializer(serializers.ModelSerializer):
    class Meta:
        model = DraftPick
        fields = '__all__'