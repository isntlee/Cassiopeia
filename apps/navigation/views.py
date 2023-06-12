from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .models import  Waypoint, Trait
from testing.views import get_request


class WaypointCreateView(CreateView):
    model = Waypoint
    fields = []
    
    def form_valid(self, form):
        home_system = 'X1-HQ18'
        location  = 'X1-HQ18-57781A' 
        url = f"https://api.spacetraders.io/v2/systems/{home_system}/waypoints"
        info  = get_request(url)

        data = info.get('data', [])
        for waypoint in data:
            waypoint_name = waypoint['symbol']
            waypoint_obj = Waypoint.objects.filter(symbol=waypoint_name).first()

            if waypoint_obj:
                continue
            else: 
                new_waypoint = Waypoint.objects.create(
                                    symbol = waypoint_name,
                                    systemSymbol = waypoint['systemSymbol'],
                                    type = waypoint['type'],
                                    coords_long = waypoint['x'],
                                    coords_lat = waypoint['y'],
                                    faction = waypoint['faction']['symbol']
                            )  

            for trait in waypoint['traits']:
                trait_symbol = trait['symbol']
                trait_obj, created  = Trait.objects.get_or_create(symbol=trait_symbol)
                new_waypoint.traits.add(trait_obj) 

        return super().form_valid(form)
        
    def get_success_url(self):
        return reverse_lazy('about')
    
    template_name = 'navigation/testing.html'


# Probably goin to require object class??
def find_destinations(system, waypoint_type):
    for waypoint in Waypoint.objects.filter(systemSymbol=system):
        for trait in waypoint.traits.all():
            if trait.symbol == waypoint_type:
                print('\n\n', waypoint.waypoint_name, '\n\n')
                destinations = [].append(waypoint)
                return destinations
            
