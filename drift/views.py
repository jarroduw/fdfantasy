import random
import hashlib
from collections import OrderedDict

from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm
from django.core.mail import send_mail

from django.db.models import Sum
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render
from django_tables2 import RequestConfig
from django.template import Context
from django.template.loader import get_template
from django.utils import timezone
from django.urls import reverse
from django.views import View
from django.contrib.auth import authenticate, login
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

# Create your views here.
from django.conf import settings
from drift.models import *
from drift.forms import *
from drift.tables import *
from drift.api import *

class ActivateEmailView(View):

    def get(self, request, nonce):
        d = UserDetail.objects.filter(nonce=nonce)[0]
        d.activated = True
        d.save()
        return HttpResponseRedirect(reverse('drift:home'))

class RegisterAccountView(View):

    def post(self, request, user_id=None):
        '''need to post data'''

        if user_id is not None:
            user = User.objects.get(id=user_id)
            signUpForm = EditAccountForm(request.POST, instance=user)
            edit = True
        else:
            edit = False
            signUpForm = SignUpForm(request.POST)

        if signUpForm.is_valid():
            if edit:
                print(signUpForm)
                user = signUpForm.save()
                return HttpResponseRedirect(reverse('drift:account'))
            else:
                matchingEmail = User.objects.filter(email=signUpForm.cleaned_data['email'])
                if len(matchingEmail) > 0:
                    signUpForm.add_error(None, "A user with that email already exists")
                
                if len(matchingEmail) == 0:
                    user = signUpForm.save()
                    ud = UserDetail.objects.create(user=user, nonce=int(random.uniform(1000000000, 10000000000000000)))
                    ud.save()

                    if not edit:

                        new_user = authenticate(
                            username=signUpForm.cleaned_data['username'],
                            password=signUpForm.cleaned_data['password1'],
                            )
                        login(request, new_user)
                        adminUser = User.objects.filter(username='admin')[0]
                        email_msg = get_template(
                            'drift/email_activateEmail.html'
                            ).render({
                                'nonce': ud.nonce,
                                'user': request.user,
                                'baseUrl': settings.ROOT_URL
                                })
                        send_mail(
                            "FD Fantasy Activation",
                            email_msg,
                            settings.DEFAULT_FROM_EMAIL,
                            [new_user.email]
                            )
                        note = Notification.objects.create(
                            user=new_user,
                            sender=adminUser,
                            msg='Welcome to FD Fantasy!'
                        )
                        note.save()
                    return HttpResponseRedirect(reverse('drift:home'))

        context = {
            'signUpForm': signUpForm,
            }

        return render(request, 'drift/register.html', context=context)

    def get(self, request, user_id=None):

        form = SignUpForm()
        if request.user.is_authenticated:
            user = User.objects.get(id=user_id)
            if user == request.user:
                form = EditAccountForm(None, instance=user)

        context = {
            'signUpForm': form,
            }

        return render(request, 'drift/register.html', context=context)

class ChangePasswordView(View):
    def post(self, request):
        '''need to post data'''

        form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            change = form.save()
            return HttpResponseRedirect(reverse('drift:home'))

        context = {}
        context['form'] = PasswordChangeForm(user=request.user)
        return render(request, 'drift/changePassword.html', context=context)

    def get(self, request):
        form = PasswordChangeForm(user=request.user)

        context = {'form': form}

        return render(request, 'drift/changePassword.html', context=context)
    

class UpcomingEvent(object):

    def __init__(self, title, date, url=None):
        self.title = title
        self.date = date
        self.url = url

def getUpcoming(user):
    timeNow = timezone.now()
    eventLi = []
    teams = Team.objects.filter(owner=user)
    leagues = set([x.league for x in teams])

    draft = [x.draftdate for x in leagues if x.draftdate.draft >= timeNow]
    draft = [
        UpcomingEvent(
            'Draft',
            x.draft,
            reverse('drift:league', args=[x.league.id])
            ) for x in draft
        ]
    eventLi.extend(draft)

    races = Event.objects.filter(end__gte=timeNow).order_by('start')
    if len(races) > 0:
        races = races[0:min([len(races), 3])]
        races = [
            UpcomingEvent(
                x.name,
                x.start,
                reverse('drift:viewEvent', args=[x.id])
                ) for x in races
            ]
        eventLi.extend(races)

    return eventLi

class UserDashboardView(View):

    def get(self, request):
        """Need to return some general links"""

        if request.user.is_authenticated:

            teams = Team.objects.filter(owner=request.user.id)

            leagues = set([t.league for t in teams])
            upcoming = getUpcoming(request.user)
            notifications = Notification.objects.filter(
                user=request.user
                ).order_by('-created_at')

            context = {
                'teams': teams,
                'leagues': leagues,
                'upcoming': upcoming,
                'notifications': notifications,
            }

        else:
            context = {'form': AuthenticationForm}

        return render(request, 'drift/userDashboard.html', context=context)

class AllLeagues(View):

    def get(self, request):
        leagues = League.objects.all()

        try:
            myLeague = request.user.league_set.all()
        except:
            myLeague = None

        try:
            myTeams = request.user.team_set.all()
            myTeamsDic = {}
            for team in myTeams:
                if team.league.name not in myTeamsDic.keys():
                    myTeamsDic[team.league.name] = team
            myTeams = [val for key,val in myTeamsDic.items()]
        except:
            myTeams = None

        context = {
            'leagues': leagues,
            'myLeagues': myLeague,
            'myTeams': myTeams
        }

        return render(request, 'drift/leagues.html', context=context)

def draftInFuture(league):
    return timezone.now() < league.draftdate.draft


class CreateLeagueView(View):

    def post(self, request, league_id=None):
        """Save new or updated league"""

        active_season = Season.objects.filter(active=True).latest('end')

        if league_id is not None:
            league = League.objects.get(id=league_id)
            form1 = LeagueForm(request.POST, instance=league)
            form2 = DraftDateForm(request.POST, instance=league.draftdate)

        else:
            form1 = LeagueForm(request.POST)
            form2 = DraftDateForm(request.POST)
        if form1.is_valid():
            if form2.is_valid():
                if form2.cleaned_data['draft'] >= timezone.now():
                    league = form1.save(commit=False)
                    league.race_official = request.user
                    league.season = active_season
                    league.save()
                    
                    draft = form2.save(commit=False)
                    draft.league = league
                    draft.save()
                    return HttpResponseRedirect(reverse('drift:league', args=[league.id]))
                else:
                    form2.add_error(None, 'Draft must be in future')
        context = {'leagueForm': form1, 'draftForm': form2}
        return render(request, 'drift/createLeague.html', context=context)

    def get(self, request, league_id=None):
        if league_id is not None:
            league = League.objects.get(id=league_id)
            form1 = LeagueForm(None, instance=league)
            form2 = DraftDateForm(None, instance=league.draftdate)

        else:
            form1 = LeagueForm()
            form2 = DraftDateForm()

        context = {'leagueForm': form1, 'draftForm': form2}

        return render(request, 'drift/createLeague.html', context=context)

class InviteUsersToJoinLeague(View):

    def post(self, request, league_id):
        league = League.objects.get(id=league_id)

        form = InviteUserForm(request.POST)

        if form.is_valid():

            now = timezone.now()
            msg = '%s - %s - %s' % (form.cleaned_data['email'], league.id, now,)
            msg = msg.encode('utf-8')
            key_code = hashlib.md5(msg).hexdigest()

            invite = form.save(commit=False)
            invite.key_code = key_code
            invite.league = league
            invite.save()

            email_msg = get_template('drift/email_leagueInvite.html').render(
                {
                    'baseUrl': settings.ROOT_URL,
                    'joinCode': invite.key_code,
                    'user': request.user,
                    'league_id': league_id
                }
            )

            send_mail(
                "FD Fantasy League Invite - %s" % (league.name,),
                email_msg,
                settings.DEFAULT_FROM_EMAIL,
                [invite.email]
            )

            return HttpResponseRedirect(reverse('drift:league', args=[league_id]))

        context = {'form': form, 'league': league}
        return render(request, 'drift/createInvites.html', context=context)

    def get(self, request, league_id):
        league = League.objects.get(id=league_id)

        form = InviteUserForm()

        context = {
            'form': form,
            'league': league
        }

        return render(request, 'drift/createInvites.html', context=context)


class LeagueView(View):

    def get(self, request, pk):
        """Should show your league, if no league redirecto to join/create"""

        league = League.objects.get(id=pk)
        openInvites = LeagueInvite.objects.filter(league=league, used=False).order_by('created_at')

        openInvitesDic = {}
        for invite in openInvites:
            if invite.email not in openInvitesDic.keys():
                openInvitesDic[invite.email] = invite
        openInvites = [val for key, val in openInvitesDic.items()]

        context = {
            'league': league,
            'draftInFuture': draftInFuture(league),
            'openInvites': openInvites
            }

        return render(request, 'drift/league.html', context=context)

    def post(self):
        """"Should save a new league with corresponding rules"""

class UserAccountView(View):

    def get(self, request):
        """Should show account view"""
        user = User.objects.get(pk=request.user.id)

        return render(request, 'drift/user.html', context={'user': user})

    def post(self):
        """Should allow user to register and save a bunch of stuff"""

class RacerListView(View):

    def get(self, request):

        racers = Racer.objects.all().order_by('name')

        context = {'drivers': racers}

        return render(request, 'drift/racersList.html', context)

class RacerView(View):

    def get(self, request, pk):
        """Will return a racer view"""

        active_season = Season.objects.filter(active=True).latest('end')

        context = {
            'driver': Racer.objects.get(pk=pk),
            'ranking': Ranking.objects.filter(racer=pk, season=active_season).latest('created_at'),
            }
        races = Race.objects.filter(top_seed=pk) | Race.objects.filter(bottom_seed=pk)
        races = races.order_by('event', '-event_round')
        newRaces = {}
        for race in races:
            try:
                newRaces[race.event.name].append(race)
            except KeyError:
                newRaces[race.event.name] = [race]
        context['races'] = newRaces

        context['championships'] = races.filter(event_round = 2)

        return render(request, 'drift/racer.html', context)

class ManufacturerTeamView(View):
    
    def get(self, request, teamName=None):
        """See a given manufacturer's racers"""

        racers = Racer.objects.all().order_by('car_manuf', 'name')

        if teamName is not None:
            racers = racers.filter(car_manuf=teamName)

        teams = OrderedDict()
        for racer in racers:
            try:
                teams[racer.car_manuf].append(racer)
            except KeyError:
                teams[racer.car_manuf] = [racer]
        
        context = {
            'teams': teams,
            'racers': racers,
            'facetBy': 'Manufacturer',
            'teamName': teamName
        }

        return render(request, 'drift/teamView.html', context)

class CreateFantasyTeam(View):
    def post(self, request, team_id=None, key_code=None, league_id=None):
        """Save new or updated team"""

        key_code_error = ''

        validationRequired = True
        form = TeamForm(request.POST)
        if team_id is not None:
            team = Team.objects.get(id=team_id)
            form = TeamForm(request.POST, instance=league)
            validationRequired = False

        if form.is_valid():
            if not form.cleaned_data['league'].key_required:
                validationRequired = False
            key_code = form.cleaned_data['key_code']
            key_code_obj = LeagueInvite.objects.filter(key_code=key_code).order_by('-created_at')
            if len(key_code_obj) > 0 or not validationRequired:
                try:
                    key_code_obj = key_code_obj[0]
                    if key_code_obj.league == form.cleaned_data['league']:
                        print("It matches!")
                        key_code_obj.used = True
                        key_code_obj.save()
                    else:
                        print("No match!")
                        key_code_error += 'That key code is not valid for this league.'
                except IndexError:
                    pass
                if key_code_error == '':
                    team = form.save(commit=False)
                    team.owner = request.user
                    team.save()
                    return HttpResponseRedirect(reverse('drift:viewFantasyTeam', args=[team.id]))
            else:
                key_code_error += 'That key code is not valid. Please check your email or contact your league race official.'
            
        if key_code_error is not None:
                form.add_error(None, key_code_error)

        context = {'form': form}
        return render(request, 'drift/createTeam.html', context=context)

    def get(self, request, team_id=None, key_code=None, league_id=None):
        if team_id is not None:
            team = Team.objects.get(id=team_id)
            form = TeamForm(None, instance=team)

        preFill = {}

        if key_code is not None:
            preFill['key_code'] = key_code

        if league_id is not None:
            try:
                league = League.objects.get(pk=league_id)
                preFill['league'] = league
            except League.DoesNotExist:
                pass

        if len(preFill) != 0:
            form = TeamForm(preFill)
        else:
            form = TeamForm()

        context = {'form': form,}

        return render(request, 'drift/createTeam.html', context=context)

class TeamView(View):
    
    def get(self, request, teamName=None):
        """See a given team's racers"""

        racers = Racer.objects.all().order_by('team_name', 'name')

        owner = False
        if teamName is not None:
            racers = racers.filter(team_name=teamName)

        teams = OrderedDict()
        for racer in racers:
            try:
                teams[racer.team_name].append(racer)
            except KeyError:
                teams[racer.team_name] = [racer]
        
        context = {
            'teams': teams,
            'racers': racers,
            'facetBy': 'Team',
            'teamName': teamName,
            'owner': owner
        }

        return render(request, 'drift/teamView.html', context)

class ListEventsView(View):

    ##TODO: Scraper is not getting right location and dates at least in post

    def get(self, request):
        """See a list of all events"""

        active_season = Season.objects.filter(active=True).latest('end')
        events = Event.objects.filter(season=active_season)

        return render(request, 'drift/eventsList.html', {'events': events})

class EventView(View):

    def get(self, request, pk):
        """See a given event and any plans/results"""

        event = Event.objects.get(pk=pk)

        qualify_latest = Qualify.objects.latest('scraped')
        qualify = Qualify.objects.filter(event=pk, scraped=qualify_latest.scraped).order_by('rank')
        qualify_pro = qualify.filter(pro2=False)
        qualify_pro2 = qualify.filter(pro2=True)

        races_latest = Race.objects.latest('scraped')
        races = Race.objects.filter(event=pk, scraped=races_latest.scraped).order_by('-event_round')
        races_pro2 = races.filter(pro2=True)
        races_pro = races.filter(pro2=False)
        races2_pro = {
            '32': races_pro.filter(event_round = 32),
            '16': races_pro.filter(event_round = 16),
            '8': races_pro.filter(event_round=8),
            '4': races_pro.filter(event_round=4),
            '2': races_pro.filter(event_round=2)
        }
        races2_pro2 = {
            '32': races_pro2.filter(event_round = 32),
            '16': races_pro2.filter(event_round = 16),
            '8': races_pro2.filter(event_round=8),
            '4': races_pro2.filter(event_round=4),
            '2': races_pro2.filter(event_round=2)
        }

        context = {'event': event, 'qualify_pro': qualify_pro, 'qualify_pro2': qualify_pro2, 'races_pro': races2_pro, 'races_pro2': races2_pro2}
        
        return render(request, 'drift/event.html', context)

class AboutView(View):

    def get(self, request):
        """Loads an about page"""

        return render(request, 'drift/about.html', {})

class MyFantasyTeams(View):

    def get(self, request):

        active_season = Season.objects.filter(active=True).latest('end')
        if request.user.is_authenticated:
            teams = Team.objects.filter(owner=request.user, league__season=active_season)
        else:
            teams = []

        if len(teams) == 0:
            teams = Team.objects.all()
            noTeams = True
        else:
            noTeams = False

        context = {'teams': teams, 'noTeams': noTeams}

        return render(request, 'drift/myteams.html', context)

class TeamRacerObject(object):
    """Holds data about a racer to make presentation easier"""

    def __init__(self, racer, team_id, event):
        self.team = Team.objects.get(pk=team_id)
        self.racer = racer
        self.id = self.racer.id

        points = self.racer.scoringevent_set.filter(event__end__lte=event.end)
        self.allPoints = sum([x.value.points for x in points])
        self.eventPoints = sum([x.value.points for x in points.filter(event=event)])

class ViewFantasyTeam(View):
    ##View by event, if same day or later than event start, show active, but not writeable
    ##  if before event start, show active, make writeable
    ##  if after event start, show active, but not writeable
    ##DEFAULT=next event, based on end


    def get(self, request, team_id, event_id=None):

        currentDate = timezone.now().date()

        team = Team.objects.get(id=team_id)

        events = Event.objects.filter(season=team.league.season)
        nextEvent = events.filter(end__gte=currentDate).order_by('start')
        if len(nextEvent) > 0:
            nextEvent = nextEvent[0]
        else:
            nextEvent = None

        if event_id is None:
            try:
                eventData = events.filter(end__gt=currentDate).latest('end')
            except Event.DoesNotExist:
                eventData = events.latest('end')
        else:
            eventData = Event.objects.get(pk=event_id)

        context = self._getActiveInactive(team_id, eventData)

        writeable = False
        if request.user == context['team'].owner and eventData.start >= currentDate:
            writeable = True
        context['writeable'] = writeable
        context['draftInFuture'] = draftInFuture(team.league)
        context['owner'] = request.user == team.owner
        context['events'] = events
        context['nextEvent'] = nextEvent

        context['totalPoints'] = {
            'active': {
                'allPoints': sum([x.allPoints for x in context['active']]),
                'eventPoints': sum([x.eventPoints for x in context['active']]),
            },
            'inactive': {
                'allPoints': sum([x.allPoints for x in context['inactive']]),
                'eventPoints': sum([x.eventPoints for x in context['inactive']]),
            }
        }

        return render(request, 'drift/viewTeam.html', context)

    def _getActiveInactive(self, team_id, event):
        teamData = Team.objects.get(pk=team_id)
        teamActive = TeamActive.objects.filter(team=teamData, modified_at__lte=event.start)

        racerDict = {}
        active = []
        inactive = []
        for racer in [x.racer for x in teamActive]:
            racerObj = TeamRacerObject(racer, team_id, event)
            try:
                test = racerDict[racer]
            except KeyError:
                racerDict[racer] = 1
                temp = teamActive.filter(racer=racer).latest('modified_at')
                if racer in teamData.racers.all() and temp.status:
                    active.append(racerObj)

        for racer in teamData.racers.all():
            racerObj = TeamRacerObject(racer, team_id, event)
            if racer not in active:
                inactive.append(racerObj)

        return {'team': teamData, 'active': active, 'inactive': inactive}

class AcquireDriver(View):

    def get(self, request, league_id):

        if not request.user.is_authenticated:
            return HttpResponseRedirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

        league = League.objects.get(pk=league_id)
        teams = league.team_set.all()
        owners = [team.owner for team in teams]
        if request.user not in owners:
            raise django.core.exceptions.PermissionDenied

        ownerTeam = request.user.team_set.filter(league=league_id)[0]

        unavailableList = getUnavailableDrivers(league)
        for team in league.team_set.all():
            for racer in team.racers.all():
                unavailableList.append(racer.id)

        available = Racer.objects.all().exclude(id__in=unavailableList)
        availableTable = RacerTableLeague(available, team=ownerTeam)
        RequestConfig(request, paginate=False).configure(availableTable)

        waiverDrivers = ownerTeam.waiverwire_set.filter(active=True)

        context = {
            'available': availableTable,
            'owner': request.user,
            'team': ownerTeam,
            'league': league,
            'waiverDrivers': waiverDrivers,
            'waiverOrder': ownerTeam.waiverpriority.getLeagueOrderTeams()
        }

        return render(request, 'drift/acquireDriver.html', context)

def getUnavailableDrivers(league):
    unavailableList = []
    for team in league.team_set.all():
        for racer in team.racers.all():
            unavailableList.append(racer.id)
    return unavailableList

class AddDriverToWaiverWire(View):

    def post(self, request, driver_id, team_id):
        """This will be where we save the person to drop"""
        errorMsg = ""

        team = Team.objects.get(pk=team_id)
        if team.owner != request.user:
            raise django.core.exceptions.PermissionDenied

        racerToAdd = Racer.objects.get(pk=driver_id)
        league = team.league
        if racerToAdd.id in getUnavailableDrivers(league):
            return HttpResponseBadRequest()

        waiverPriority = team.waiverpriority.firstInOrder()

        pks = request.POST.getlist("drop")
        added = False
        remaining = len(team.racers.all()) - len(pks)
        if remaining < league.max_racers:
            with transaction.atomic():
                for pk in pks:
                    racer = Racer.objects.get(pk=pk)
                    if racer in team.racers.all():
                        if waiverPriority == True:
                            team.racers.remove(racer)
                            if not added:
                                addRacerToTeam(team, racerToAdd)
                                added = True
                        else:
                            if not added:
                                ww = addRacerToWaiver(team, racerToAdd)
                                added = True
                            wwr = WaiverWireRemove.objects.create(
                                waiver=ww,
                                racer=racer
                            )
                            wwr.save()
                    else:
                        raise django.core.exceptions.PermissionDenied
                return HttpResponseRedirect(reverse('drift:acquireDriver', args=[league.id]))

        else:
            diff = len(team.racers.all()) - league.max_racers + 1
            if diff == 1:
                msg = "1 driver"
            else:
                msg = "%s drivers" % (diff,)
            errorMsg += "You have to select at least %s to drop before you can add this driver." % (msg,)

        racers = RacerTableDrop(team.racers.all())
        RequestConfig(request, paginate=False).configure(racers)

        context = {
            'team': team,
            'racers': racers,
            'league': team.league,
            'driver': racerToAdd,
            'waiverOrder': team.waiverpriority.getLeagueOrderTeams(),
            'errorMsg': errorMsg
        }

        return render(request, 'drift/waiveRacer.html', context)

    def get(self, request, driver_id, team_id):

        team = Team.objects.get(pk=team_id)
        if team.owner != request.user:
            raise django.core.exceptions.PermissionDenied

        waiverPriority = team.waiverpriority
        
        driver = Racer.objects.get(pk=driver_id)
        league = team.league
        if driver.id in getUnavailableDrivers(league):
            return HttpResponseBadRequest()

        teamsInLeague = [team.id for team in league.team_set.all()]

        ##If no chance you'll get the driver
        claimed_li = WaiverWire.objects.filter(racer=driver_id, active=False, team__in=teamsInLeague)
        waiverWinners = [x for x in claimed_li if x.priority < waiverPriority.priority]
        claimed = False
        if len(waiverWinners) > 0:
            claimed = True

        waiverTime = timezone.now() + datetime.timedelta(league.waiver_hours*60*60)
        print("Write before does not exist")
        ##If waiver already exists, just bypass things
        try:
            wwExists = len(team.waiverwire_set.filter(active=True, racer=driver)) > 0
            if wwExists:
                return HttpResponseRedirect(reverse('drift:acquireDriver', args=[league.id]))
        except ObjectDoesNotExist:
            wwExists = False
        print(wwExists)

        ##Guaranteed to acquire acquire, change waiver order, redirect
        notFull = len(team.racers.all()) < league.max_racers
        waiverOrder = waiverPriority.getLeagueOrderTeams()
        waiverPriorityWin = waiverPriority.firstInOrder()
        with transaction.atomic():
            if notFull and waiverPriorityWin:
                addRacerToTeam(team, driver, waiverPriority)
                return HttpResponseRedirect(reverse('drift:acquireDriver', args=[league.id]))

            ##Team not full, but not first in waiver priority: 
            if notFull and not waiverPriorityWin:
                ww = addRacerToWaiver(team, driver)
                return HttpResponseRedirect(reverse('drift:acquireDriver', args=[league.id]))

        racers = RacerTableDrop(team.racers.all())
        RequestConfig(request, paginate=False).configure(racers)

        context = {
            'team': team,
            'racers': racers,
            'league': league,
            'driver': driver,
            'waiverOrder': waiverOrder
        }

        return render(request, 'drift/waiveRacer.html', context)

class TradeView(View):

    def post(self, request, team, racer):
        '''Saves trade with both teams/drivers'''
        ##TODO:
        # check user is in league
        # check that owner owns team
        # check that user selected a player
        # save to trades model, many to many on racers
        # send notification to user

    def get(self, request, team, racer=None):
        '''shows all available teams for trade'''

        ##TODO:
        ## check user is in league
        ## check that user owns team
        ## if racer is None
        ##   show all not accepted trades proposed to you
        ##   show all not accepted trades proposed by you
        ##   show all available players (i.e. not yet accepted) with option to trade
        ## else:
        #    check user is in league
        #    check user owns team
        #    show all racers on team as table with trade button

class AcceptTradeView(View):

    def post(self, request, trade, accept):
        '''Functionality to accept a trade'''
        ##TODO:
        # check user owns receiving team
        # within transaction
        #   set trade active to false
        #   if accept == True:
        #       add receiving team racer to proposing team
        #       add offering team racer to accepting team
        #       notify offering team
        #   if accept == False:
        #       notify offering team

class MessageOtherTeam(View):
    permissions = [IsAuthenticated]

    def post(self, request, team_id, sendTo=None):
        '''Validates form and saves message and sends email'''
        team = Team.objects.get(pk=team_id)
        form = MessageTeamForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.sender = request.user
            note.save()
            email_msg = get_template('drift/email_sendMessage.html').render(
                {
                    'baseUrl': settings.ROOT_URL,
                    'note': note,
                    'user': request.user
                }
            )
            send_mail(
                "FD Fantasy Activation",
                email_msg,
                settings.DEFAULT_FROM_EMAIL,
                [note.user.email]
                )
            return HttpResponseRedirect(reverse('drift:viewFantasyTeam', args=[team_id]))

        return render(request, 'drift/sendMessage.html', context)

    def get(self, request, team_id, sendTo=None):
        '''Creates form to send a message'''
        
        team = Team.objects.get(pk=team_id)
        if request.user != team.owner:
            raise PermissionDenied

        formContext = {}
        if sendTo is not None:
            sendToTeam = Team.objects.get(pk=sendTo)
            formContext['user'] = sendToTeam.owner

        teamOwners = [x.owner for x in team.league.team_set.all() if x.owner != request.user]
        form = MessageTeamForm(initial=formContext)

        context = {'form': form}
        return render(request, 'drift/sendMessage.html', context)

##TODO: Need draft view (JS)
