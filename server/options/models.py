from django.db import models


class SysOptions(models.Model):
    key = models.TextField(unique=True, db_index=True)
    value = models.JSONField()
