from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .models import Agent
from apps.testing.views import get_request, post_request


class AgentCreateView(CreateView):
    model = Agent
    fields = []
    
    def form_valid(self, form):
        url = f"https://api.spacetraders.io/v2/register"
        exp_status = 'register'
        payload = {
            "faction": "COSMIC",
            "symbol": "TESTING108",
            "email": "ninenine@testing.com"
        }

        info  = post_request(url, payload, exp_status)
        # print('\n\n User : ', self.request.user, '\n\n')
        # print('\n\n Agent: ', self.request.user.agent, '\n\n')
        data = info['data']
        agent_data = data['agent']
        agent_obj = Agent.objects.filter(symbol=agent_data['symbol']).first()

        if agent_obj:
            pass
        else: 
            Agent.objects.create(
                symbol = agent_data['symbol'],
                accountId = agent_data['accountId'],
                hq = agent_data['headquarters'],
                faction = agent_data['startingFaction'],
                credits = agent_data['credits'],
                agent_token = data['token'],
                user =  self.request.user,
            )  

        return super().form_valid(form)
        
    def get_success_url(self):
        return reverse_lazy('about')
    
    template_name = 'agents/testing.html'
