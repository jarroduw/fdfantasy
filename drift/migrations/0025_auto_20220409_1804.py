# Generated by Django 2.2.6 on 2022-04-09 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drift', '0024_auto_20200328_2047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scoringvalue',
            name='award',
            field=models.TextField(choices=[('win', 'W'), ('qualify-position', 'QP'), ('top-32', 'T32'), ('top-16', 'T16'), ('top-8', 'T8'), ('quarters', 'T4'), ('final', 'T2'), ('pro2-bonus', 'pro2-bonus')]),
        ),
        migrations.AlterField(
            model_name='scoringvalue',
            name='points',
            field=models.FloatField(),
        ),
    ]
