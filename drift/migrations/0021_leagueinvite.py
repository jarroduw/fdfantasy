# Generated by Django 2.2.6 on 2020-02-17 01:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drift', '0020_auto_20200217_0131'),
    ]

    operations = [
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
