# Generated by Django 2.2.6 on 2020-02-19 07:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drift', '0021_leagueinvite'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='key_required',
            field=models.BooleanField(default=True),
        ),
    ]