import django_tables2 as tables
from django.urls import reverse
from django.utils.html import format_html
from drift.models import *
from drift.urls import *

class RacerTable(tables.Table):
    driver_url_slug = tables.Column(verbose_name='FD Bio')
    pro2 = tables.Column(verbose_name='Class')
    latest_ranking = tables.Column(verbose_name='Ranking', accessor='getLatestRanking')
    #id = tables.Column(verbose_name='')

    def __init__(self, *args, team=None, **kwargs):
        super(RacerTable, self).__init__(*args, **kwargs)
        self.team = team

    def render_pro2(self, value, record):
        lic = 'Pro'
        if value:
            lic = 'Pro 2'
        return format_html('{}', lic)

    def render_driver_url_slug(self, value, record):
        return format_html('<a href="https://formulad.com{}">Bio</a>', value)

    def order_latest_ranking(self, queryset, is_descending):
        queryset = sorted(queryset, key=lambda x: x.getLatestRanking(), reverse=is_descending)
        return (queryset, True,)


    class Meta:
        model = Racer
        exclude = ['created_at', 'modified_at']
        attrs = {'class': 'table'}
        sequence = ('...', 'driver_url_slug')


class RacerTableLeague(RacerTable):
    id = tables.Column(verbose_name='')

    def render_id(self, value, record):
        link = reverse('drift:waiveDriver', args=[record.id, self.team.id])
        #link = '#'

        return format_html('<a href="{}" class="btn btn-primary">Acquire</a>', link)

    class Meta:
        model = Racer
        exclude = ['created_at', 'modified_at']
        attrs = {'class': 'table'}
        sequence = ('id', '...', 'driver_url_slug')

class CheckBoxColumnWithName(tables.CheckBoxColumn):

    @property
    def header(self):
        return self.verbose_name

class RacerTableDrop(RacerTable):
    drop = CheckBoxColumnWithName(verbose_name='Drop', accessor='pk')

    class Meta:
        model = Racer
        exclude = ['id', 'created_at', 'modified_at']
        attrs = {'class': 'table'}
        sequence = ('drop', '...', 'driver_url_slug')

class RacerTableTrade(RacerTable):
    id = tables.Column(verbose_name='')

    def render_id(self, value, record):
        link = reverse('drift:trade', args=[self.team.id, record.id])
        return format_html('<a href="{}" class="btn btn-primary">Request Trade</a>', link)

    class Meta:
        model = Racer
        exclude = ['created_at', 'modified_at']
        attrs = {'class': 'table'}
        sequence = ('id', '...', 'driver_url_slug')

class TradeTable(tables.Table):
    racerIn = tables.Column(verbose_name='Trade Details')

    def render_proposer(self, value, record):
        return format_html("{}", value.owner.username)

    def render_proposedTo(self, value, record):
        return format_html("{}", value.owner.username)

    def render_racerIn(self, value, record):
        racersIn = [x.name for x in value.all()]
        racersOut = [x.name for x in record.racersOut.all()]
        return format_html("{} for {}", ", ".join(racersIn), ", ".join(racersOut))

    class Meta:
        model = Trade
        exclude = ['id', 'created_at', 'modified_at', 'season']
        attrs = {'class': 'table'}

class TradeTableByMe(TradeTable):
    id = tables.Column(verbose_name='')

    def render_id(self, value, record):
        link = reverse('drift:decideTrade', args=[value, 'False'])
        return format_html('<a href="{}" class="btn btn-primary">Cancel</a>', link)

    class Meta:
        model = Trade
        exclude = ['created_at', 'proposer', 'modified_at', 'season', 'active', 'accepted']
        attrs = {'class': 'table'}

class TradeTableToMe(TradeTable):
    id = tables.Column(verbose_name='')

    def render_id(self, value, record):
        link = reverse('drift:decideTrade', args=[value, 'True'])
        link2 = reverse('drift:decideTrade', args=[value, 'False'])
        return format_html('<a href="{}" class="btn btn-primary">Accept</a><a href="{}" class="btn btn-primary">Reject</a>', link, link2)

    class Meta:
        model = Trade
        exclude = ['created_at', 'proposedTo', 'modified_at', 'season', 'active', 'accepted']
        attrs = {'class': 'table'}