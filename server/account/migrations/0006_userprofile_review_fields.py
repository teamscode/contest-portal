from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_userprofile_source'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='downvotes',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='hidden',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='upvotes',
            field=models.IntegerField(default=0),
        ),
    ]
