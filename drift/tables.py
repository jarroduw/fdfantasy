import django_tables2 as tables
from django.urls import reverse
from django.utils.html import format_html
from drift.models import *
from drift.urls import *

class RacerTable(tables.Table):
    driver_url_slug = tables.Column(verbose_name='FD Bio')
    pro2 = tables.Column(verbose_name='Class')
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