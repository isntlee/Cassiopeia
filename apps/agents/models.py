from django.db import models
from gemini.users.models import User


class Agent(models.Model):
    symbol = models.CharField(max_length=60)
    accountId = models.CharField(max_length=60)
    hq = models.CharField(max_length=60)
    faction = models.CharField(max_length=60)
    current_ship = models.CharField(max_length=60, null=True, blank=True)
    credits = models.IntegerField(null=True, blank=True)
    agent_token = models.CharField(max_length=1000)
    user = models.OneToOneField(User, related_name='agent', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.symbol:
            return
        super(Agent, self).save(*args, **kwargs)

    def __str__(self):
        return self.symbol