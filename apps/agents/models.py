from django.db import models
from gemini.users.models import User


class Agent(models.Model):
    symbol = models.CharField(max_length=60, default='symbol_default')
    accountId = models.CharField(max_length=60, default='accountId_default')
    hq = models.CharField(max_length=60, default='hq_default')
    faction = models.CharField(max_length=60, default='faction_default')
    credits = models.IntegerField(null=True, blank=True)
    agent_token = models.CharField(max_length=1000, default='token_default')
    user = models.OneToOneField(User, related_name='agent', on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.symbol:
            return
        super(Agent, self).save(*args, **kwargs)

    def __str__(self):
        return self.symbol