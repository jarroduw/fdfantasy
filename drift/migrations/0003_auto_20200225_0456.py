# Generated by Django 2.2.6 on 2020-02-25 04:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drift', '0002_auto_20200225_0421'),
    ]

    operations = [
        migrations.AddField(
            model_name='season',
            name='active',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='season',
            name='name',
            field=models.TextField(),
        ),
    ]