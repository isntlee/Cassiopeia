from datetime import datetime, timedelta
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from .models import Ship, Cargo
from apps.testing.views import get_request


def current_ship_data(data):
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

        fuel_current = data['fuel']['current']
        fuel_capacity =  data['fuel']['capacity']
        fuel_consumed =  data['fuel']['consumed']['amount']

        ship_status = data['nav']['status']
        flightmode = data['nav']['flightMode']

        arrival_time = datetime.strptime(data['nav']['route']['arrival'],"%Y-%m-%dT%H:%M:%S.%fZ")
        arrival_time += timedelta(hours=1)
        current_time = datetime.now()
        
        if arrival_time and arrival_time > current_time:
            location_current = 'IN-TRANSIT'
            location_current_type = ''
        elif arrival_time and arrival_time < current_time:
            location_current = destination_symbol
            location_current_type = destination_type
        else:
            location_current = destination_symbol
            location_current_type = 'HOME'

        return {
                'departure_symbol': departure_symbol,
                'departure_type': departure_type,
                'departure_longitude': departure_longitude,
                'departure_latitude': departure_latitude,
                'destination_symbol': destination_symbol,
                'destination_type': destination_type,
                'destination_longitude': destination_longitude,
                'destination_latitude': destination_latitude,
                'fuel_consumed': fuel_consumed,
                'fuel_capacity': fuel_capacity,
                'fuel_current': fuel_current,
                'flightmode': flightmode,
                'ship_status': ship_status,
                'location_current': location_current,
                'location_current_type': location_current_type,
                }


class ShipCreateView(CreateView):
    model = Ship
    fields = []
    template_name = 'ships/testing.html'
    
    def form_valid(self, form):
        ship_symbol = 'MEDLOCK-1'
        url = f"https://api.spacetraders.io/v2/my/ships/{ship_symbol}"

        info  = get_request(url)
        data = info.get('data', [])
        data_current = current_ship_data(data)
        
        ship_name = data['symbol']
        faction = data['registration']['factionSymbol']
        role = data['registration']['role']
 
        prev_obj = Ship.objects.filter(ship_name=ship_name).first()

        if prev_obj:
            ShipUpdateView.update_ship(self, prev_obj.pk, data_current)
            return redirect('about')

        else:
            ship_obj = Ship.objects.create(   
                **data_current,
                ship_name=ship_name,
                faction=faction,
                role=role
            )        
            ship_obj.save()

            return super().form_valid(form)
        
    def get_success_url(self):
        return reverse_lazy('about')
    

class ShipUpdateView(UpdateView):
    model = Ship
    fields = []
    template_name = 'ships/testing.html'

    def update_ship(self, ship_pk, data_current):
        Ship.objects.filter(pk=ship_pk).update(**data_current)

    def get_success_url(self):
        return reverse_lazy('about')
    

class CargoCreateView(CreateView):
    model = Cargo
    fields = []
    
    def form_valid(self, form):
        shipSymbol = 'MEDLOCK-1' 
        url = f"https://api.spacetraders.io/v2/my/ships/{shipSymbol}/cargo"
        info  = get_request(url)

        data = info.get('data', [])
        cargo_capacity = data['capacity']
        units_held = data['units']
        cargo_fill = units_held/cargo_capacity
        
        if cargo_fill == 1.00:
            full_cargo = True
        else: 
            full_cargo = False

        cargo_name = f"{shipSymbol}-cargo"
        ship_obj = Ship.objects.filter(ship_name=shipSymbol).first()
        cargo_obj = Cargo.objects.filter(cargo_name=cargo_name).first()

        if cargo_obj:
            CargoUpdateView.update_cargo(self, cargo_obj.id, cargo_capacity, units_held, cargo_fill, full_cargo)
            return redirect('about')
        else:
            cargo_obj = Cargo.objects.create(
                cargo_name = cargo_name,
                cargo_capacity=cargo_capacity,
                units_held=units_held,
                cargo_fill = cargo_fill, 
                full_cargo=full_cargo, 
                ship=ship_obj,
        ) 
        
        return super().form_valid(form)
        
    def get_success_url(self):
        return reverse_lazy('about')
    
    template_name = 'navigation/testing.html'


class CargoUpdateView(UpdateView):
    model = Cargo
    fields = []
    template_name = 'navigation/testing.html'

    def update_cargo(self, cargo_obj_pk, cargo_capacity, units_held, cargo_fill, full_cargo):
        filtered = Cargo.objects.filter(pk=cargo_obj_pk)
        filtered.update(
            cargo_capacity=cargo_capacity,
            units_held=units_held,
            cargo_fill=cargo_fill,
            full_cargo=full_cargo
        )

    def get_success_url(self):
        return 


def create_ship_or_cargo(request):
    if request.method == 'POST':
        if 'create_ship' in request.POST:
            view = ShipCreateView.as_view()
            response = view(request)
            return response
        
        elif 'create_cargo' in request.POST:
            view = CargoCreateView.as_view()
            response = view(request)
            return response
        
    return render(request, 'ships/testing.html')