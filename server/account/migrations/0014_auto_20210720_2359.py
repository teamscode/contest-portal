# Generated by Django 2.1.7 on 2021-07-20 23:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0013_auto_20210719_0506'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='real_name',
            new_name='team_members',
        ),
    ]