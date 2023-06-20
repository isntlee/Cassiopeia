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
        # get the request URL data
        ship_symbol = self.request.user.agent.current_ship
        url = f"https://api.spacetraders.io/v2/my/ships/{ship_symbol}/extract"
        payload = {}

        ################## MUST REMOVE: exp_status variable #########################
        ################## AND: all the initial error chacking ######################
        exp_status = 201

        agent_token = self.request.user.agent.agent_token
        info = post_request(url, payload, exp_status, agent_token)

        try:
            data = info.get('data', KeyError)
            extraction = data['extraction']

            ship = extraction['shipSymbol']
            extracted = extraction['yield']['symbol']
            units = extraction['yield']['units']
            cooldown = data['cooldown']['expiration']

            extraction_obj = Extraction.objects.create(
                ship=ship,
                extracted=extracted,
                units=units,
                cooldown=cooldown,
            )        

            extraction_obj.save()
            return super().form_valid(form)
        
        except Exception:
           return call_messages(self.request, info)


    def get_success_url(self):
        # redirect to a success page after data is saved
        return reverse_lazy('home')

    template_name = 'extractions/testing.html'


class ExtractionListView(ListView):
    model = Extraction
    fields = []
    template_name = 'extractions/testing.html'
