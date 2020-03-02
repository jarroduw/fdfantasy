from django import forms

from django.contrib.auth.models import User

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from drift.models import *


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )

class EditAccountForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', )

class LeagueForm(forms.ModelForm):
    name = forms.CharField(max_length=30, required=True, help_text='Required')
    class Meta:
        model = League
        fields = ['name', 'key_required']

class DateInput(forms.DateInput):
    input_type = 'date'

class DraftDateForm(forms.ModelForm):
    draft = forms.SplitDateTimeField(widget=forms.SplitDateTimeWidget, required=True, help_text='Required, use YYYY-MM-DD and HH:MM')
    class Meta:
        model = DraftDate
        fields = ['draft']

class TeamForm(forms.ModelForm):
    name = forms.CharField(max_length=30, required=True, help_text='Required')
    key_code = forms.CharField(max_length=32, required=False, help_text='Required. Check email.')
    class Meta:
        model = Team
        fields = ['league', 'key_code', 'name']

class InviteUserForm(forms.ModelForm):
    email = forms.CharField(max_length=30, required=True, help_text='Required')
    class Meta:
        model = LeagueInvite
        fields = ['email']

class MessageTeamForm(forms.ModelForm):

    class Meta:
        model = Notification
        fields = ['user', 'msg']

class TradeForm(forms.ModelForm):
    deadline = forms.SplitDateTimeField(widget=forms.SplitDateTimeWidget, required=True, help_text='Required, use YYYY-MM-DD and HH:MM')

    class Meta:
        model = Trade
        fields = ['deadline']