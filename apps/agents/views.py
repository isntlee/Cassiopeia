from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.views.generic import CreateView, UpdateView, ListView
from .models import Agent
from testing.views import get_request, post_request


class AgentCreateView(CreateView):
    model = Agent
    fields = []
    template_name = 'agents/testing.html'
    
    def form_valid(self, form):
        try: 
            url = f"https://api.spacetraders.io/v2/register"
            exp_status = 'register'
            payload = {
                "faction": "COSMIC",
                "symbol": "TESTING115",
                "email": "testing@testing.com"
            }
            agent_token = self.request.user.agents.first().agent_token
            info = post_request(url, payload, exp_status, agent_token)
            data = info['data']
            agent_data = data['agent']

        except Exception:
            url = f"https://api.spacetraders.io/v2/my/agent"
            agent_choice = 0
            user_token = Agent.objects.all()[agent_choice].agent_token
            info = get_request(url, user_token)
            agent_data = info['data']
   
        agent_obj = Agent.objects.filter(symbol=agent_data['symbol']).first()
        credits = agent_data['credits']

        if agent_obj:
            AgentUpdateView.update_agent(self, agent_obj.pk, credits)    
        else:
            Agent.objects.create(
                symbol = agent_data['symbol'],
                accountId = agent_data['accountId'],
                hq = agent_data['headquarters'],
                faction = agent_data['startingFaction'],
                credits = credits,
                agent_token = data['token'],
                user =  self.request.user,
            )

        return super().form_valid(form)
        
    def get_success_url(self):
        return reverse_lazy('about')
    

class AgentUpdateView(UpdateView):
    model = Agent
    fields = []
    template_name = 'agents/testing.html'

    def update_agent(self, agent_obj_pk, credits):
        update_obj = Agent.objects.filter(pk=agent_obj_pk)
        update_obj.update(
            credits = credits,
        )

    def get_success_url(self):
        return 


class AgentListView(ListView):
    model = Agent
    fields = []
    template_name = 'agents/testing.html'
