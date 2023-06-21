from datetime import datetime, timedelta
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView
from apps.markets.models import Good
from .models import Ship, Cargo, CargoLoad
from testing.views import get_request, call_messages


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
        agent = self.request.user.agent
        ship_symbol = agent.current_ship
        url = f"https://api.spacetraders.io/v2/my/ships/{ship_symbol}"

        agent_token =  agent.agent_token
        info = get_request(url, agent_token)
        try: 

            data = info.get('data', [])
            data_current = current_ship_data(data)
            
            ship_name = data['symbol']
            faction = data['registration']['factionSymbol']
            role = data['registration']['role']
    
            prev_obj = Ship.objects.filter(ship_name=ship_name).first()

            if prev_obj:
                ShipUpdateView.update_ship(self, prev_obj.pk, data_current)
                return redirect('ships:ship_list')

            else:
                ship_obj = Ship.objects.create(   
                    **data_current,
                    ship_name=ship_name,
                    faction=faction,
                    role=role
                )        
                ship_obj.save()

                return super().form_valid(form)
        
        except Exception:
           return call_messages(self.request, info)
        
    def get_success_url(self):
        return reverse_lazy('ships:ship_list')
    

class ShipUpdateView(UpdateView):
    model = Ship
    fields = []
    template_name = 'ships/testing.html'

    def update_ship(self, ship_pk, data_current):
        Ship.objects.filter(pk=ship_pk).update(**data_current)

    def get_success_url(self):
        return reverse_lazy('ships:ship_list')
    

class CargoCreateView(CreateView):
    model = Cargo
    fields = []

    def get_cargo_data(self, agent, current_ship):
        url = f"https://api.spacetraders.io/v2/my/ships/{current_ship}/cargo"
        agent_token = self.request.user.agent.agent_token
        info = get_request(url, agent_token)
        data = info.get('data', [])
        return data

    def calculate_cargo_fill(self, cargo_capacity, units_held):
        cargo_fill = units_held / cargo_capacity
        full_cargo = cargo_fill == 1.00
        return cargo_fill, full_cargo

    def create_or_update_cargo(self, cargo_load_list, cargo_obj, current_ship, cargo_capacity, units_held, cargo_fill, full_cargo):
        ship_obj = Ship.objects.filter(ship_name=current_ship).first()
        if cargo_obj:
            self.create_or_update_cargoload(cargo_load_list, cargo_obj)
            CargoUpdateView.update_cargo(self, cargo_obj.id, cargo_capacity, units_held, cargo_fill, full_cargo)
        else:
            cargo_name = f"{current_ship}-cargo"
            cargo_obj = Cargo.objects.create(
                cargo_name=cargo_name,
                cargo_capacity=cargo_capacity,
                units_held=units_held,
                cargo_fill=cargo_fill,
                full_cargo=full_cargo,
                ship=ship_obj,
            )

    def form_valid(self, form):
        agent = self.request.user.agent
        current_ship = agent.current_ship
        cargo_data = self.get_cargo_data(agent, current_ship)

        try:
            cargo_capacity = cargo_data['capacity']
            units_held = cargo_data['units']
            cargo_fill, full_cargo = self.calculate_cargo_fill(cargo_capacity, units_held)

            cargo_name = f"{current_ship}-cargo"
            cargo_load_list = cargo_data['inventory']
            cargo_obj = Cargo.objects.filter(cargo_name=cargo_name).first()

            self.create_or_update_cargo(cargo_load_list, cargo_obj, current_ship, cargo_capacity, units_held, cargo_fill, full_cargo)
            return super().form_valid(form)

        except Exception:
            return call_messages(self.request, cargo_data)

         
    def create_or_update_cargoload(self, cargo_load_list, cargo_obj):
        for cargo_load in cargo_load_list:
            current_cargo_load_obj = CargoLoad.objects.filter(symbol=cargo_load['symbol'], cargo=cargo_obj).first()
            
            # Add the delete cargoload function after sell functions built in

            if current_cargo_load_obj:
                    current_cargo_load_obj.units = cargo_load['units']
                    current_cargo_load_obj.save()

            else:  
                good_obj = Good.objects.filter(symbol=cargo_load['symbol']).first() 

                if good_obj is None:
                    good_obj = Good.objects.create(symbol=cargo_load['symbol'], name=cargo_load['name'], description=cargo_load['description'])
                    good_obj.save()

                cargoload_obj = CargoLoad.objects.create(
                        symbol = cargo_load['symbol'],
                        units = cargo_load['units'],
                        good = good_obj,
                        cargo = cargo_obj
                ) 
                cargoload_obj.save() 
        
    def get_success_url(self):
        return reverse_lazy('ships:ship_list')
        
    template_name = 'navigation/testing.html'


class CargoUpdateView(UpdateView):
    model = Cargo
    fields = []
    template_name = 'navigation/testing.html'

    def update_cargo(self, cargo_pk, cargo_capacity, units_held, cargo_fill, full_cargo):
        filtered = Cargo.objects.filter(pk=cargo_pk)
        filtered.update(
            cargo_capacity=cargo_capacity,
            units_held=units_held,
            cargo_fill=cargo_fill,
            full_cargo=full_cargo
        )

    def get_success_url(self):
        return 
    

class ShipListView(ListView):
    model = Ship
    fields = []
    template_name = 'ships/testing.html'


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



