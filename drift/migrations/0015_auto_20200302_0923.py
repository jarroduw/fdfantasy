# Generated by Django 2.2.6 on 2020-03-02 09:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drift', '0014_auto_20200302_0144'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='draftorder',
            name='owner',
        ),
        migrations.AddField(
            model_name='draftdate',
            name='started',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='draftorder',
            name='team',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to='drift.Team'),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='DraftPick',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('selected_at', models.DateTimeField()),
                ('draft_order', models.IntegerField()),
                ('draft', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='drift.DraftDate')),
                ('racer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='drift.Racer')),
                ('team', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='drift.Team')),
            ],
        ),
    ]
