import datetime

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class League(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    name = models.TextField()
    race_official = models.ForeignKey(User, models.SET_NULL, blank=True, null=True)
    key_required = models.BooleanField(default=True, verbose_name="Require a key to join?")

    def __str__(self):
        return "%s-%s" % (self.race_official, self.name,)

class UserDetail(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    user = models.OneToOneField(User, models.CASCADE)
    nonce = models.TextField()
    activated = models.BooleanField(default=False)

    def __str__(self):
        return "%s" % (self.user,)

class Racer(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    name = models.TextField()
    team_name = models.TextField(blank=True)
    driver_url_slug = models.TextField()
    car_number = models.IntegerField()
    car_manuf = models.TextField()

    def getAllPoints(self):
        data = ScoringEvent.objects.filter(racer=self.id)

    def __str__(self):
        return '%s' % (self.name,)

class Ranking(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    racer = models.ForeignKey(Racer, models.CASCADE)
    rank = models.IntegerField()
    points = models.IntegerField(null=True)

    def __str__(self):
        return "%s - %s - %s" % (self.racer, self.rank, self.created_at,)

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

    def __str__(self):
        return '%s - %s - %s' % (self.event, self.racer, self.rank,)

class Race(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    event = models.ForeignKey(Event, models.CASCADE)
    event_round = models.IntegerField()
    top_seed = models.ForeignKey(Racer, models.CASCADE, related_name='%(class)s_racer_top_seed')
    bottom_seed = models.ForeignKey(Racer, models.CASCADE, related_name='%(class)s_racer_bottom_seed', null=True)
    winner = models.ForeignKey(Racer, models.CASCADE, related_name='%(class)s_racer_winner', null=True)

    def __str__(self):
        return '%s (%s) - %s' % (self.event, self.event_round, self.winner,)

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
    league = models.ForeignKey(League, models.CASCADE)
    award = models.TextField(choices=AWARDS)
    points = models.IntegerField()

    def __str__(self):
        return '%s - %s' % (self.league, self.award,)

class Team(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    league = models.ForeignKey(League, models.SET_NULL, blank=True, null=True)
    owner = models.ForeignKey(User, models.CASCADE)
    name = models.TextField()
    racers = models.ManyToManyField(Racer)

    def __str__(self):
        return '%s - (%s, %s)' % (self.name, self.league, self.owner,)

class ScoringEvent(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    team = models.ForeignKey(Team, models.CASCADE)
    racer = models.ForeignKey(Racer, models.CASCADE, null=True)
    event = models.ForeignKey(Event, models.CASCADE)
    value = models.ForeignKey(ScoringValue, models.CASCADE)

    def __str__(self):
        return '%s - %s - %s' % (self.event, self.team, self.racer,)

class TeamActive(models.Model):
    modified_at = models.DateTimeField(auto_now=True)
    team = models.ForeignKey(Team, models.CASCADE)
    racer = models.ForeignKey(Racer, models.CASCADE)
    status = models.BooleanField(default=False)

    def __str__(self):
        return '%s - %s (%s)' % (self.team, self.racer, self.status,)

class MatchupSeed(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    league = models.ForeignKey(League, models.SET_NULL, blank=True, null=True)
    owner = models.OneToOneField(User, models.CASCADE)
    seed = models.IntegerField()

    def __str__(self):
        return '%s - %s (%s)' % (self.league, self.owner, self.seed,)

class DraftOrder(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    league = models.ForeignKey(League, models.SET_NULL, blank=True, null=True)
    owner = models.OneToOneField(User, models.CASCADE)
    seed = models.IntegerField()

    def __str__(self):
        return '%s - %s (%s)' % (self.league, self.owner, self.seed,)

class DraftDate(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    league = models.OneToOneField(League, models.CASCADE)
    draft = models.DateTimeField(verbose_name="Date of Draft")

    def __str__(self):
        return '%s - %s' % (self.league, self.draft,)

class Notification(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    read = models.BooleanField(default=False)
    user = models.ForeignKey(User, models.CASCADE,  related_name='%(class)s_user')
    sender = models.ForeignKey(User, models.SET_NULL, null=True,  related_name='%(class)s_sender')
    msg = models.TextField()

    def isModified(self):
        return roundTime(self.created_at) != roundTime(self.modified_at)

    def __str__(self):
        return '%s - %s, %s (%s)' % (self.sender, self.user, self.created_at, self.modified_at,)

class LeagueInvite(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    used = models.BooleanField(default=False)
    league = models.ForeignKey(League, models.CASCADE)
    email = models.TextField()
    key_code = models.TextField()

    def __str__(self):
        return '%s - %s (%s)' % (self.league, self.email, self.key_code,)

def roundTime(dt=None, dateDelta=60):
    """Round a datetime object to a multiple of a timedelta
    dt : datetime.datetime object, default now.
    dateDelta : timedelta object, we round to a multiple of this, default 1 minute.
    Author: Thierry Husson 2012 - Use it as you want but don't blame me.
            Stijn Nevens 2014 - Changed to use only datetime objects as variables
    """
    roundTo = datetime.timedelta(seconds=dateDelta).total_seconds()

    if dt == None : 
        dt = timezone.now()
    #Make sure dt and datetime.min have the same timezone
    tzmin = dt.min.replace(tzinfo=dt.tzinfo)

    seconds = (dt - tzmin).seconds
    # // is a floor division, not a comment on following line:
    rounding = (seconds+roundTo/2) // roundTo * roundTo
    return dt + datetime.timedelta(0,rounding-seconds,-dt.microsecond)

##TODO: Deploy to AWS, need HTTPS, backups to S3
##TODO: Add a "Season" class, and associate with team/league
##TODO: Add current and last season stats for racer overview
##TODO: Add ability to add driver from 'undrafted list's
##TODO: Add draft?
##TODO: Add communiction module TO ENABLE:
##  TODO: Propose/Accept trade
##TODO: Implement waiver wire restrictions: need waiver order and one-day to one-week delay