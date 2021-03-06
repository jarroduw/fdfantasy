# Generated by Django 2.2.6 on 2020-02-22 22:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('drift', '0001_initial'), ('drift', '0002_event_location'), ('drift', '0003_auto_20191228_2320'), ('drift', '0004_auto_20191228_2322'), ('drift', '0005_auto_20191228_2358'), ('drift', '0006_auto_20191229_0002'), ('drift', '0007_auto_20191229_1727'), ('drift', '0008_auto_20191229_1756'), ('drift', '0009_teamactive'), ('drift', '0010_auto_20200201_0535'), ('drift', '0011_draftdate_draftorder_matchupseed'), ('drift', '0012_scoringevent'), ('drift', '0013_auto_20200215_1717'), ('drift', '0014_scoringevent_racer'), ('drift', '0015_notification'), ('drift', '0016_remove_userdetail_league'), ('drift', '0017_userdetail_nonce'), ('drift', '0018_auto_20200216_1136'), ('drift', '0019_auto_20200216_1744'), ('drift', '0020_auto_20200217_0131'), ('drift', '0021_leagueinvite'), ('drift', '0022_league_key_required')]

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('schedule_url_slug', models.TextField()),
                ('name', models.TextField()),
                ('address', models.TextField(null=True)),
                ('start', models.DateField()),
                ('end', models.DateField()),
                ('location', models.TextField(default='something')),
            ],
        ),
        migrations.CreateModel(
            name='League',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.TextField()),
                ('race_official', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('key_required', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Racer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.TextField()),
                ('team_name', models.TextField(blank=True)),
                ('driver_url_slug', models.TextField()),
                ('car_number', models.IntegerField()),
                ('car_manuf', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.TextField()),
                ('league', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='drift.League')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('racers', models.ManyToManyField(to='drift.Racer')),
            ],
        ),
        migrations.CreateModel(
            name='ScoringValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('award', models.TextField(choices=[('win', 'win'), ('qualify', 'quality'), ('qualify-position', 'qualify-position'), ('top-32', 'top-32'), ('top-16', 'top-16'), ('top-8', 'top-8'), ('quarters', 'quarters'), ('final', 'final'), ('podium', 'podium'), ('one-more-time', 'one-more-time'), ('checked-in', 'checked-in'), ('clean-sweep', 'clean-sweep')])),
                ('points', models.IntegerField()),
                ('league', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='drift.League')),
            ],
        ),
        migrations.CreateModel(
            name='Qualify',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('rank', models.IntegerField()),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='drift.Event')),
                ('racer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='drift.Racer')),
            ],
        ),
        migrations.CreateModel(
            name='Ranking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('rank', models.IntegerField()),
                ('points', models.IntegerField(null=True)),
                ('racer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='drift.Racer')),
            ],
        ),
        migrations.CreateModel(
            name='Race',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('bottom_seed', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='race_racer_bottom_seed', to='drift.Racer')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='drift.Event')),
                ('top_seed', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='race_racer_top_seed', to='drift.Racer')),
                ('winner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='race_racer_winner', to='drift.Racer')),
                ('event_round', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='TeamActive',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('status', models.BooleanField(default=False)),
                ('racer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='drift.Racer')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='drift.Team')),
            ],
        ),
        migrations.CreateModel(
            name='MatchupSeed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('seed', models.IntegerField()),
                ('league', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='drift.League')),
                ('owner', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DraftOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('seed', models.IntegerField()),
                ('league', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='drift.League')),
                ('owner', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DraftDate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('draft', models.DateTimeField(verbose_name='Date of Draft')),
                ('league', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='drift.League')),
            ],
        ),
        migrations.CreateModel(
            name='ScoringEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='drift.Event')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='drift.Team')),
                ('value', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='drift.ScoringValue')),
                ('racer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='drift.Racer')),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('read', models.BooleanField(default=False)),
                ('msg', models.TextField()),
                ('sender', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notification_sender', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notification_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('nonce', models.TextField(default=1)),
                ('activated', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='LeagueInvite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('used', models.BooleanField(default=False)),
                ('email', models.TextField()),
                ('key_code', models.TextField()),
                ('league', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='drift.League')),
            ],
        ),
    ]
