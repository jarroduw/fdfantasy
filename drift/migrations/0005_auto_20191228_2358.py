# Generated by Django 2.2.6 on 2019-12-28 23:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drift', '0004_auto_20191228_2322'),
    ]

    operations = [
        migrations.AlterField(
            model_name='racer',
            name='team_name',
            field=models.TextField(blank=True),
        ),
    ]
