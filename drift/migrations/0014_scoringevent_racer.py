# Generated by Django 2.2.6 on 2020-02-16 00:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drift', '0013_auto_20200215_1717'),
    ]

    operations = [
        migrations.AddField(
            model_name='scoringevent',
            name='racer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='drift.Racer'),
        ),
    ]