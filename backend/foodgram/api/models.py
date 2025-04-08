from django.db import models


class BlacklistedTokens(models.Model):
    token = models.TextField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
