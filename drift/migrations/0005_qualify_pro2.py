# Generated by Django 2.2.6 on 2020-02-25 06:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drift', '0004_race_pro2'),
    ]

    operations = [
        migrations.AddField(
            model_name='qualify',
            name='pro2',
            field=models.BooleanField(default=False),
        ),
    ]
