# Generated by Django 2.2.6 on 2020-03-02 01:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drift', '0013_trade_proposedto'),
    ]

    operations = [
        migrations.AddField(
            model_name='trade',
            name='accepted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='trade',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
