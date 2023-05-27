from django.shortcuts import render

# Create your views here.
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import Ship
from apps.testing.views import get_request
from datetime import datetime


class ShipCreateView(CreateView):
    model = Ship
    fields = []
    template_name = 'ships/testing.html'
    
    def form_valid(self, form):
        ship_symbol = 'MEDLOCK-1'
        url = f"https://api.spacetraders.io/v2/my/ships/{ship_symbol}"

        info  = get_request(url)
        data = info.get('data', [])
        
        ship_name = data['symbol']
        faction = data['registration']['factionSymbol']
        role = data['registration']['role']

        departure = data['nav']['route']['departure']
        departure_symbol = departure['symbol']
        departure_type = departure['type']
        departure_longitude = departure['x']
        departure_latitude = departure['y']
        
        
        destination = data['nav']['route']['destination']
        destination_symbol = destination['symbol']
        destination_type = destination['type']
        destination_longitude = destination['x']
        destination_latitude = destination['y']

        arrival_time = datetime.strptime(data['nav']['route']['arrival'],"%Y-%m-%dT%H:%M:%S.%fZ")
        current_time = datetime.now()
        
        if arrival_time and arrival_time > current_time:
            location_current = 'IN-TRANSIT'
        elif arrival_time:
            location_current = f"{destination_type}:{destination_symbol}"
        else:
            location_current = f"HOME:{destination_symbol}"

        ship_status = data['nav']['status']
        flightmode = data['nav']['flightMode']

        fuel_current = data['fuel']['current']
        fuel_capacity =  data['fuel']['capacity']
        fuel_consumed =  data['fuel']['consumed']['amount']

        ship_obj = Ship.objects.create(
            ship_name=ship_name,
            faction=faction,
            role=role,
            departure_symbol=departure_symbol,
            departure_type=departure_type,
            departure_longitude = departure_longitude, 
            departure_latitude=departure_latitude,
            destination_symbol=destination_symbol,
            destination_type=destination_type,
            destination_longitude=destination_longitude,
            destination_latitude=destination_latitude,
            fuel_current=fuel_current,
            fuel_capacity=fuel_capacity,
            fuel_consumed=fuel_consumed,
        )        
        ship_obj.save()

        return super().form_valid(form)

    def get_success_url(self):
        # redirect to a success page after data is saved
        return reverse_lazy('about')

    