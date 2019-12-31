from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class League(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    name = models.TextField()
    race_official = models.OneToOneField(User, models.SET_NULL, blank=True, null=True)

class UserDetail(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    user = models.OneToOneField(User, models.CASCADE)
    league = models.ForeignKey(League, models.SET_NULL, blank=True, null=True)
    birthdate = models.DateField()

class Racer(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    name = models.TextField()
    team_name = models.TextField(blank=True)
    driver_url_slug = models.TextField()
    car_number = models.IntegerField()
    car_manuf = models.TextField()

    def __str__(self):
        return '%s' % (self.name,)

class Ranking(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    racer = models.ForeignKey(Racer, models.CASCADE)
    rank = models.IntegerField()
    points = models.IntegerField(null=True)

class Event(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    schedule_url_slug = models.TextField()
    name = models.TextField()
    location = models.TextField()
    address = models.TextField(null=True)
    start = models.DateField()
    end = models.DateField()

    def __str__(self):
        return '%s - %s' % (self.name, self.start,)

class Qualify(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    event = models.ForeignKey(Event, models.CASCADE)
    racer = models.ForeignKey(Racer, models.CASCADE)
    rank = models.IntegerField()

class Race(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    event = models.ForeignKey(Event, models.CASCADE)
    event_round = models.IntegerField()
    top_seed = models.ForeignKey(Racer, models.CASCADE, related_name='%(class)s_racer_top_seed')
    bottom_seed = models.ForeignKey(Racer, models.CASCADE, related_name='%(class)s_racer_bottom_seed', null=True)
    winner = models.ForeignKey(Racer, models.CASCADE, related_name='%(class)s_racer_winner', null=True)

class ScoringValue(models.Model):
    AWARDS = (
        ('win', 'win',),
        ('qualify', 'quality',),
        ('qualify-position', 'qualify-position'),
        ('top-32', 'top-32'),
        ('top-16', 'top-16'),
        ('top-8', 'top-8',),
        ('quarters', 'quarters',),
        ('final', 'final',),
        ('podium', 'podium',),
        ('one-more-time', 'one-more-time',),
        ('checked-in', 'checked-in',),
        ('clean-sweep', 'clean-sweep',)
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    league = models.OneToOneField(League, models.CASCADE)
    award = models.TextField(choices=AWARDS)
    points = models.IntegerField()

class Team(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    league = models.OneToOneField(League, models.SET_NULL, blank=True, null=True)
    owner = models.OneToOneField(User, models.CASCADE)
    name = models.TextField()
    racers = models.ManyToManyField(Racer)
