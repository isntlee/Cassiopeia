from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.views.generic import CreateView, UpdateView, ListView
from .models import Agent
from testing.views import get_request, post_request, call_messages


class AgentCreateView(CreateView):
    model = Agent
    fields = []
    template_name = 'agents/testing.html'
    
    def form_valid(self, form):
        agent_obj = self.request.user.agents.first()
        
        if agent_obj:
            url = f"https://api.spacetraders.io/v2/my/agent"
            info = get_request(url, agent_obj.agent_token)
            info['data']['status'] = 'updated'
            self.info = info
            agent_data = info.get('data', KeyError)
            AgentUpdateView.update_agent(self, agent_obj.pk, agent_data['credits'])

        else: 
            url = f"https://api.spacetraders.io/v2/register"
            exp_status = 'register'
            symbol = "TESTING115"
            payload = {
                "faction": "COSMIC",
                "symbol": symbol,
                "email": "testing@testing.com"
            } 
            info = post_request(url, payload, exp_status, agent_obj.agent_token)

            try:
                data = info.get('data', KeyError)
                Agent.objects.create(
                    symbol = agent_data['symbol'],
                    accountId = agent_data['accountId'],
                    hq = agent_data['headquarters'],
                    faction = agent_data['startingFaction'],
                    credits = credits,
                    agent_token = data['token'],
                    user =  self.request.user,
                )
            except Exception:
                call_messages(self.request, info)
    
        return super().form_valid(form)
        
    def get_success_url(self):
        return reverse_lazy('home')
    

class AgentUpdateView(UpdateView):
    model = Agent
    fields = []
    template_name = 'agents/testing.html'

    def update_agent(self, agent_obj_pk, credits):
        update_obj = Agent.objects.filter(pk=agent_obj_pk)
        update_obj.update(
            credits = credits,
        )
        call_messages(self.request, self.info)   

    def get_success_url(self): 
        return 


class AgentListView(ListView):
    model = Agent
    fields = []
    template_name = 'agents/testing.html'
