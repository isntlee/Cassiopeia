from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import Extraction
from apps.testing.views import post_request


class ExtractionCreateView(CreateView):
    model = Extraction
    fields = []
    def form_valid(self, form):
        # get the request URL data
        ship_symbol = 'MEDLOCK-1'
        url = f"https://api.spacetraders.io/v2/my/ships/{ship_symbol}/extract"
        payload = {}

        ################## MUST REMOVE: exp_status variable #########################
        ################## AND: all the initial error chacking ######################
        exp_status = 201

        info  = post_request(url, payload, exp_status)
        data = info.get('data', [])
        
        extraction = data['extraction']
        ship = extraction['shipSymbol']
        extracted = extraction['yield']['symbol']
        units = extraction['yield']['units']
        cooldown = data['cooldown']['remainingSeconds']
        cargo_capacity = data['cargo']['capacity']
        units_held = data['cargo']['units']
        cargo_fill = units_held/cargo_capacity

        if cargo_fill == 1.00:
            full_cargo = True
        else: 
            full_cargo = False

        extraction_obj = Extraction.objects.create(
            ship=ship,
            extracted=extracted,
            units=units,
            cooldown=cooldown,
            cargo_capacity=cargo_capacity,
            units_held=units_held,
            cargo_fill = cargo_fill, 
            full_cargo=full_cargo
        )        

        extraction_obj.save()

        return super().form_valid(form)

    def get_success_url(self):
        # redirect to a success page after data is saved
        return reverse_lazy('about')

    template_name = 'extractions/testing.html'