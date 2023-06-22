from django.shortcuts import redirect
from django import forms
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.views.generic import CreateView, ListView, FormView, View
from .models import  Waypoint, Trait
from apps.ships.models import Ship
from testing.views import get_request, post_request, call_messages


class WaypointCreateView(CreateView):
    model = Waypoint
    fields = []
    
    def form_valid(self, form):
        agent = self.request.user.agent
        ship_obj = Ship.objects.filter(ship_name=agent.current_ship).first()
        location = ship_obj.location_current[:7] 
        url = f"https://api.spacetraders.io/v2/systems/{location}/waypoints"
        agent_token = agent.agent_token
        info = get_request(url, agent_token)

        try:
            data = info.get('data', KeyError)
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
        
        except Exception:
            return call_messages(self.request, info)
        
        
    def get_success_url(self):
        return reverse_lazy('navigation:waypoint_list')
    
    template_name = 'navigation/testing.html'


class WaypointListView(ListView):
    model = Waypoint
    fields = []
    template_name = 'navigation/testing.html'

    def get_queryset(self):
        current_ship = self.request.user.agent.current_ship
        ship_data = Ship.objects.filter(ship_name=current_ship)
        waypoint_data = Waypoint.objects.all()
        return {'waypoints': waypoint_data, 'ships': ship_data}


class NavigateFormClass(forms.Form):
    user_input = forms.CharField(label='User Input', max_length=100)


class NavigateView(FormView):
    template_name = 'navigation/testing.html'
    form_class = NavigateFormClass
    success_url = reverse_lazy('navigation:waypoint_list')

    def form_valid(self, form): 
        agent_token =  self.request.user.agent.agent_token
        ship_symbol = self.request.user.agent.current_ship
        exp_status = 200

        orbit_url = f"https://api.spacetraders.io/v2/my/ships/{ship_symbol}/orbit"
        payload = {}
        post_request(orbit_url, payload, exp_status, agent_token)

        url = f"https://api.spacetraders.io/v2/my/ships/{ship_symbol}/navigate" 
        user_input = self.request.POST.get('user_input')
        payload = {'waypointSymbol': user_input}
        post_request(url, payload, exp_status, agent_token)

        return super().form_valid(form)


class DockToggleView(View):
    template_name = 'navigation/testing.html'
    success_url = reverse_lazy('navigation:waypoint_list')

    def post(self, *args, **kwargs):
        agent = self.request.user.agent
        agent_token = agent.agent_token
        ship_symbol = agent.current_ship
        ship_data = Ship.objects.filter(ship_name=ship_symbol).first()
        exp_status = 200

        if ship_data.ship_status == 'IN_ORBIT':
            self.ship_action(agent_token, ship_symbol, exp_status, 'dock')
        
        elif ship_data.ship_status == 'DOCKED':
            self.ship_action(agent_token, ship_symbol, exp_status, 'orbit')
        
        else:
            info = {"error":{"message":"Currently in-transit, cannot dock or orbit", "code":4309}}
            call_messages(self.request, info)
        return HttpResponseRedirect(self.success_url)

    def ship_action(self, agent_token, ship_symbol, exp_status, action):
        url = f"https://api.spacetraders.io/v2/my/ships/{ship_symbol}/{action}"
        payload = {}
        post_request(url, payload, exp_status, agent_token)
