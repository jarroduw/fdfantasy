# Generated by Django 2.2.6 on 2019-12-29 00:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drift', '0005_auto_20191228_2358'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ranking',
            name='points',
            field=models.IntegerField(null=True),
        ),
    ]