# Generated by Django 2.2.6 on 2020-03-02 00:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drift', '0011_auto_20200302_0040'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trade',
            name='proposedTo',
        ),
    ]