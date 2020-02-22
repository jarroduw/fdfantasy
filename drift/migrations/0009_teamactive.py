# Generated by Django 2.2.6 on 2020-01-30 06:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drift', '0008_auto_20191229_1756'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeamActive',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('status', models.BooleanField(default=False)),
                ('racer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='drift.Racer')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='drift.Team')),
            ],
        ),
    ]
