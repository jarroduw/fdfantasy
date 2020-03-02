# Generated by Django 2.2.6 on 2020-03-02 00:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drift', '0012_remove_trade_proposedto'),
    ]

    operations = [
        migrations.AddField(
            model_name='trade',
            name='proposedTo',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='trade_team_proposedTo', to='drift.Team'),
        ),
    ]
