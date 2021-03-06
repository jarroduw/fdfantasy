# Generated by Django 2.2.6 on 2020-02-28 05:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drift', '0007_racer_pro2'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='draft_interval_minutes',
            field=models.IntegerField(default=4),
        ),
        migrations.AddField(
            model_name='league',
            name='max_racers',
            field=models.IntegerField(default=12),
        ),
        migrations.AddField(
            model_name='league',
            name='waiver_hours',
            field=models.IntegerField(default=24),
        ),
        migrations.CreateModel(
            name='WaiverWire',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('racer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='drift.Racer')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='drift.Team')),
            ],
        ),
        migrations.CreateModel(
            name='WaiverPriority',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('priority', models.IntegerField()),
                ('team', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='drift.Team')),
            ],
        ),
    ]
