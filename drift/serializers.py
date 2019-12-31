from drift.models import *
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