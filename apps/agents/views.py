from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.views.generic import CreateView, UpdateView, ListView
from .models import Agent
from apps.ships.views import ShipCreateView
from testing.views import get_request, post_request, call_messages


class AgentCreateView(CreateView):
    model = Agent
    fields = []
    template_name = 'agents/testing.html'

    def form_valid(self, form):
        if hasattr(self.request.user, 'agent'):
            agent_obj = self.request.user.agent
            self.update_agent(agent_obj)
        else:
            self.create_agent()
        return super().form_valid(form)

    def update_agent(self, agent_obj):
        if agent_obj:
            url = "https://api.spacetraders.io/v2/my/agent"
            info = get_request(url, agent_obj.agent_token)
            info['data']['status'] = 'updated'
            self.info = info
            agent_data = info.get('data', KeyError)
            AgentUpdateView.update_agent(self, agent_obj.pk, agent_data['credits'])

    def create_agent(self):
        url = "https://api.spacetraders.io/v2/register"
        exp_status = 'register'
        symbol = "Gentry"
        agent_token = None
        payload = {
            "faction": "COSMIC",
            "symbol": symbol,
            "email": "testing@testing.com"
        }
        info = post_request(url, payload, exp_status, agent_token)

        try:
            data = info.get('data', KeyError)
            Agent.objects.create(
                symbol=data['agent']['symbol'],
                accountId=data['agent']['accountId'],
                hq=data['agent']['headquarters'],
                faction=data['agent']['startingFaction'],
                current_ship=data['ship']['symbol'],
                credits=data['agent']['credits'],
                agent_token=data['token'],
                user=self.request.user,
            )
            ShipCreateView.as_view()
        except Exception:
            call_messages(self.request, info)

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
