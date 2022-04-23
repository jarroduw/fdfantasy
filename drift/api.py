import logging
logger = logging.getLogger(__name__)
import random

import time
import datetime

from huey.contrib.djhuey import HUEY

from django.db import transaction
from django.conf import settings
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.template.loader import get_template
from django.utils.timesince import timesince

from huey import crontab
from huey.contrib.djhuey import db_task, db_periodic_task, revoke_by_id, is_revoked

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
        if 'get_latest' in data.keys():
            result = Event.objects.filter(
                end__gte=datetime.datetime.utcnow()
                ).order_by('end').first()
        else:
            result = Event.objects.filter(**data).first()
        serializer = EventSerializer(result)
        return Response(serializer.data)

class QualifyApi(APIView):
    permission_classes = [IsAuthenticated|ReadOnly]
    def post(self, request, format=None):
        """API call to set the qualify rank"""

        data = request.data
        scraped_date = data['scraped']
        del data['scraped']
        result = Qualify.objects.filter(**data).all()
        
        if len(result) > 0:
            logger.debug("FOUND EXISTING QUALIFY RECORD")
            ## If records exist, skip over
            serializer_exists = QualifySerializer(result.first())
            return Response(serializer_exists.data)
        ## Otherwise, add to it
        data['scraped'] = scraped_date
        serializer = QualifySerializer(data=data)
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
        result = Racer.objects.filter(**data).all()
        serializer = RacerSerializer(result, many=True)
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
        data = request.data
        scraped_date = data['scraped']
        winner = data['winner']
        del data['scraped']
        del data['winner']
        logger.debug("QUERY DATA: %s", data)
        result = Race.objects.filter(**data).all()
        logger.debug("QUERY RESULT: %s", result)
        
        if len(result) > 0:
            logger.info("FOUND EXISTING RECORD")
            ## If records exist, skip over
            if result[0].winner == winner:
                logger.info("--> Existing record has not changed")
                serializer_exists = RaceSerializer(result.first())
            else:
                logger.info("--> Existing record has changed winner, saving")
                ## Don't have a winner, going to update record and return
                temp = result.first()
                winner_obj = Racer.objects.get(pk=winner)
                temp.winner = winner_obj
                temp.save()
                temp.refresh_from_db()
                serializer_exists = RaceSerializer(temp)
            return Response(serializer_exists.data)

        ## Otherwise, add to it
        logger.debug("Adding race result")
        data['scraped'] = scraped_date
        data['winner'] = winner
        serializer = RaceSerializer(data=data)
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
            data = serializer.validated_data
            print(data)
            teamActive = TeamActive.objects.filter(team=data['team'])
            actualActive = {}
            for r in teamActive:
                try:
                    test = actualActive[r.racer]
                except KeyError:
                    d = teamActive.filter(racer=r.racer).latest('modified_at')
                    if d.status:
                        actualActive[r.racer] = d

            if len(actualActive) < data['team'].league.max_racers or not data['status']:
                serializer.save()
                return Response({'msg': 'Driver status changed'}, status=status.HTTP_201_CREATED)
            return Response({'msg': 'Too many drivers activated (%s) only %s allowed' % (len(actualActive), data['team'].league.max_racers,)}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PointsApi(APIView):
    permission_classes = [IsAuthenticated|ReadOnly]

    def get(self, request, event, team, racer):
        data = getPoints(event, racer)
        serializer = ScoringEventSerializer(data)
        return Response(serializer.data)

class Scoring(object):
    """Class defining a row of scoring data for a team"""

    def __init__(self, team_id, racer_id, event_id=None):
        self.team = team_id
        self.teamObj = Team.objects.get(pk=team_id)
        self.racer = racer_id
        self.racerObj = Racer.objects.get(pk=racer_id)
        self.event = event
        if self.event is not None:
            self.eventObj = Event.objects.get(pk=event_id)
            eventPoints = getPoints(self.event, self.racer)
            self.eventPoints = {}
            for pts in eventPoints:
                try:
                    self.eventPoints[pts.award]+=points
                except KeyError:
                    self.eventPoints[pts.award] = points
        allPoints = getAllPoints(self.racer)
        self.allPoints = {}
        for pts in allPoints:
            try:
                self.allPoints[pts.award]+=points
            except KeyError:
                self.allPoints[pts.award] = points

def getPoints(event, racer):
    data = ScoringEvent.objects.all(event=event, racer=racer)
    return data

def getAllPoints(racer):
    data = ScoringEvent.objects.all(racer=racer)
    return data

class NotificationApi(APIView):
    permission_classes = [IsAuthenticated|ReadOnly]

    def get(self, request, lastPoll=None):
        data = getNotifications(request.user)
        if lastPoll is not None:
            lastPoll = datetime.datetime.fromtimestamp(float(lastPoll))
            data = data.filter(created_at__gt=lastPoll)
        data = data.order_by('created_at')
        serializer = NotificationSerializer(data, many=True)
        return Response(serializer.data)

def getNotifications(user):
    notes = Notification.objects.filter(user=user)
    return notes

class CheckWaiverWire(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        checkWaiverWire_task.call_local()
        return Response({'msg': 'success'})

@db_periodic_task(crontab(minute='*/2'))
def checkWaiverWire_task():
    waivers = WaiverWire.objects.filter(active=True).order_by('team__waiverpriority', 'team__id')
    waivers = [x for x in waivers if x.getExpired()==True or x.team.waiverpriority.firstInOrder()==True]
    while len(waivers) > 0:
        waiver = waivers[0]
        with transaction.atomic():
            addRacerToTeam(waiver.team, waiver.racer)
            for removeRacer in waiver.waiverwireremove_set.filter(active=True):
                waiver.team.racers.remove(removeRacer.racer)
                removeRacer.active = False
                removeRacer.save()
        waivers = WaiverWire.objects.filter(active=True).order_by('team__waiverpriority', 'team__id')
        waivers = [x for x in waivers if x.getExpired()==True or x.team.waiverpriority.firstInOrder()==True]

class CheckDraftStart(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        checkDraftStartTask.call_local()        
        return Response({'msg': 'success'})

@db_periodic_task(crontab(minute='*/1'))
def checkDraftStartTask():
    now = timezone.now()
    now_plus_hour = now + datetime.timedelta(hours=1)
    drafts = DraftDate.objects.filter(draft__lte=now_plus_hour, started=False)
    for draft in drafts:
        if draft.draft <= now:
            setDraftDateActive(draft)
        elif not draft.one_hour_warning:
            setDraftDateWarning(draft)

class DraftPickAPI(APIView):
    permission_classes = [IsTeamOwner]

    def get(self, request, team_id, latest=False):
        team = Teamobjects.get(pk=team_id)
        dp = DraftPick.objects.get(league=team.league)
        if latest:
            dp = dp.latest('selected_at')
        serializer = DraftPickSerializer(dp)
        return Response(serializer.data)

    def post(self, request, team_id):
        success = None
        team = Team.objects.get(pk=team_id)
        if request.user != team.owner:
            raise PermissionDenied
        with transaction.atomic():
            thisAd = DraftPickReservation.getQueued(team.league.draftdate)
            if len(thisAd) == 0:
                raise AttributeError("There are no autodrafts queued")
            if len(thisAd) > 1:
                raise AttributeError("There are too many autodrafts queued")
            thisAd = thisAd[0]
            if thisAd.team != team:
                raise PermissionDenied
            thisAd.due_at = timezone.now()
            thisAd.save()
            success = True
        if success is None:
            return Response({'msg': 'No picks queued'})
        elif success:
            return Response({'msg': 'Saved!'})
        return Response({'msg': 'Its not your turn'})

def getAutodraftInstance(draft, tries=20):
    running = False
    n = 0
    while not running:
        ad = HUEY.scheduled()
        if len(ad) > 0:
            thisAd = [x for x in ad if x.args[1] == draft.id]
            if len(thisAd) > 0:
                thisAd = thisAd[0]
                running = True
                break
        if n >= tries:
            thisAd = None
            break
        n+=1
    return thisAd

def makeDraftPick(team_id, draft_id):
    logger.info("Making a pick for team %s", team_id)
    ## Making a draft pick
    team = Team.objects.get(pk=team_id)
    ## Figuring out draft pick context
    do = DraftOrder.objects.filter(league=team.league).order_by('seed')
    myDo = do.get(team=team)
    meIdx = list(do).index(myDo)
    ## Figure out what the last pick was
    try:
        lastPick = DraftPick.objects.filter(draft=team.league.draftdate).latest('selected_at')
        lastPickDo = do.get(team=lastPick.team)
        lastPickIdx = list(do).index(lastPickDo)
        ## Figure out if it's the first pick, or the last pick plus one
        if lastPick.pick_number < len(team.league.team_set.all()):
            pick_number = lastPick.pick_number + 1
            rd = lastPick.round
        else:
            pick_number = 1
            rd = lastPick.round + 1
    except DraftPick.DoesNotExist:
        ## For scenario where there was no last draft pick (i.e., the first pick of the draft)
        lastPick = None
        lastPickIdx = -1
        pick_number = 1
        rd = 1
    
    ## Now, assuming it's actually my turn, let's make a pick
    if meIdx - 1 == lastPickIdx or (lastPickIdx == len(do)-1 and meIdx == 0):
        now = timezone.now()
        ## Getting the draftqueue, which has my top pick in it, who i want to add to my team
        dq = team.draftqueue
        with transaction.atomic():
            if len(dq.priority) != 0:
                ## Assuming that we have someone in our draft queue
                racer_id = dq.priority.pop(0)
                racer = Racer.objects.get(pk=racer_id)
            else:
                ## Otherwise, we just take from the top of the list of undrafteds...
                do = DraftOrder.objects.filter(league=team.league)
                try:
                    ## Get all picks
                    allPicks = DraftPick.objects.filter(team__in=[x.team for x in do])
                    ## then filter out all the racers that have already been picked
                    racers = Racer.objects.all().exclude(id__in=[x.racer.id for x in allPicks])
                except DraftPick.DoesNotExist:
                    ## For the first pick...
                    racers = Racer.objects.all()
                
                ## Orders by ranking, which we don't currently have data for...
                racer = sorted(racers, key=lambda x: x.getLatestRanking(), reverse=False)[0]

            ## Actually make the pick
            dp = DraftPick.objects.create(
                draft=team.league.draftdate,
                team=team,
                selected_at=now,
                racer=racer,
                round=rd,
                pick_number=pick_number
            )
            dp.save()
            ## Add racer to team
            team.racers.add(racer)
            dq.save()
            ## Save draft queue
            for team in team.league.team_set.all():
                ## Need to drop that racer from the draft queue of all teams
                dq = team.draftqueue
                try:
                    found = dq.priority.pop(dq.priority.index(racer.id))
                    dq.save()
                    logger.info("Dropping racer from queue: %s for team: %s", racer.id, team.id)
                except ValueError:
                    pass
                ## Send notification, which will trigger a refresh of the screen
                note = Notification.objects.create(
                    user=team.owner,
                    msg='%s selected %s with pick %s of round %s.' % (
                        dp.team.owner.username,
                        dp.racer.name,
                        dp.pick_number,
                        dp.round,
                        )
                )
                note.save()
                logger.info("Finished drafting player")
        return True
    ## If it's not my turn, returning False
    return False


class QueueAPI(APIView):
    permission_classes = [IsTeamOwner|ReadOnly]

    def get(self, request, team_id):
        dq = DraftQueue.objects.get(team=team_id)
        queue = self._getRacerNamesFromQueue(dq)
        return Response(queue)

    def post(self, request, team_id, racer_id, position='add'):
        dq = DraftQueue.objects.get(team=team_id)
        alreadyThere = racer_id in dq.priority
        if position == 'bottom':
            if alreadyThere:
                temp = dq.priority.pop(dq.priority.index(racer_id))
            dq.priority.append(racer_id)
        elif position == 'top':
            temp = dq.priority.pop(dq.priority.index(racer_id))
            dq.priority = [racer_id] + dq.priority
        elif position == 'up':
            current = dq.priority.index(racer_id)
            new = current - 1
            temp = dq.priority.pop(current)
            dq.priority.insert(new, racer_id)
        elif position == 'down':
            current = dq.priority.index(racer_id)
            new = current + 1
            temp = dq.priority.pop(current)
            dq.priority.insert(new, racer_id)
        elif position == 'remove':
            temp = dq.priority.pop(dq.priority.index(racer_id))
        elif position == 'add':
            if racer_id not in dq.priority:
                dq.priority.append(racer_id)
        else:
            raise AttributeError('Action %s is not a valid update' % (position,))
        dq.save()
        queue = self._getRacerNamesFromQueue(dq)
        return Response(queue)

    def _getRacerNamesFromQueue(self, dq):
        queue = []
        for d_id in dq.priority:
            racer = Racer.objects.get(pk=d_id)
            queue.append((racer.id, racer.name,))
        return queue

def setDraftDateActive(draft):

    if not draft.started:
        with transaction.atomic():
            for team in draft.league.team_set.all():
                note = Notification.objects.create(
                    user=team.owner,
                    msg='Draft for %s league starting now!' % (team.league,)
                )
                email_msg = get_template(
                    'drift/email_draftStarting.html'
                    ).render({
                        'team': team,
                        'baseUrl': settings.ROOT_URL,
                        })
                send_mail(
                    "Draft for %s league starting!",
                    email_msg,
                    settings.DEFAULT_FROM_EMAIL,
                    [team.owner.email]
                )
            draft.started = True
            draft.save()
        import threading
        t = threading.Thread(target=startAutodraft, args=(draft,))
        t.setDaemon(True)
        t.start()
        #startAutodraft(draft)

def startAutodraft(draft):
    logger.info("Starting autodraft: %s", draft.id)
    do = DraftOrder.objects.all().order_by('seed')
    timeUntil = draft.league.draft_interval_minutes*60
    while not draft.finished:
        for d in do:
            logger.warning("Team %s on the clock and seed=%s", d.team, d.seed)
            ##Start task for team, with  countdown
            s = DraftPickReservation.schedule(draft, d.team, delay=timeUntil)
            logger.warning("Scheduled reservation for %s", d.team.id)
            ##Infinite loop for pick
            while True:
                logger.warning("Waiting for pick")
                ## Why atomic here? Seems like it would not be able to handle calls to queue
                with transaction.atomic():
                    ## Get all queued picks, then get all of them marked as expired
                    t = DraftPickReservation.getQueued(draft, expired=True)
                    if len(t) > 0:
                        logger.info("Pick made, executing draft pick for %s", d.team.id)
                        for s in t:
                            ##Execute
                            success = makeDraftPick(d.team.id, draft.id)
                            logger.info("Executed pick with success=%s", success)
                            s.active=False
                            s.save()
                        break
                time.sleep(1)
        ##Check if last pick should be final pick
        lastPick = draft.draftpick_set.latest('selected_at')
        timeUntil = draft.league.draft_interval_minutes*60 - (timezone.now() - lastPick.selected_at).seconds
        if lastPick.round == draft.league.max_racers:
            draft.finished = True
            draft.save()                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
            for d in do:
                wp = WaiverPriority.objects.create(
                    team=d.team,
                    priority=d.seed
                    )
                wp.save()
            break

def setDraftDateWarning(draft):
    if not draft.one_hour_warning:
        with transaction.atomic():
            teams = draft.league.team_set.all()
            random.shuffle(list(teams))
            for t, team in enumerate(teams):
                do, created = DraftOrder.objects.update_or_create(
                    team=team,
                    league=team.league,
                    seed=t,
                    defaults = {'team': team}
                )
                do.save()
                note = Notification.objects.create(
                    user=team.owner,
                    msg='Draft for %s league starts in %s!' % (team.league, timesince(team.league.draftdate.draft),)
                )
                email_msg = get_template(
                    'drift/email_draftStartingSoon.html'
                    ).render({
                        'team': team,
                        'baseUrl': settings.ROOT_URL,
                        })
                send_mail(
                    "Draft for %s league starts soon!",
                    email_msg,
                    settings.DEFAULT_FROM_EMAIL,
                    [team.owner.email]
                )
            draft.one_hour_warning = True
            draft.save()

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