from django.views.generic import CreateView,ListView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .models import Extraction
from testing.views import post_request, call_messages


class ExtractionCreateView(CreateView):
    model = Extraction
    fields = []
    
    def form_valid(self, form):
        agent = self.request.user.agent
        ship_symbol = agent.current_ship
        url = f"https://api.spacetraders.io/v2/my/ships/{ship_symbol}/extract"
        payload = {}

        exp_status = 201
        agent_token = agent.agent_token
        info = post_request(url, payload, exp_status, agent_token)

        try:
            data = info['data']
            extraction = data['extraction']

            ship = extraction['shipSymbol']
            extracted = data['extraction']['yield']['symbol']
            units = extraction['yield']['units']
            cooldown_from = data['cooldown']['expiration']

            extraction_obj = Extraction.objects.create(
                ship=ship,
                extracted=extracted,
                units=units,
                cooldown_from=cooldown_from,
            )
            extraction_obj.save()
            return super().form_valid(form)
        
        except Exception as e:  # Catch the exception as a variable
            print('Exception:', e)  # Print the exception details
            return call_messages(self.request, info)

    def get_success_url(self):
        return reverse_lazy('home')

    template_name = 'extractions/testing.html'


class ExtractionListView(ListView):
    model = Extraction
    fields = []
    template_name = 'extractions/testing.html'
