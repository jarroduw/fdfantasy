# Generated by Django 2.2.6 on 2020-03-06 08:40

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drift', '0017_draftqueue'),
    ]

    operations = [
        migrations.AlterField(
            model_name='draftqueue',
            name='priority',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True), default=list, size=None),
        ),
    ]
