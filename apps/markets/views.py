from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView
from .models import  Market, TradeGood, Good
from apps.ships.models import Ship
from apps.navigation.models import Waypoint
from testing.views import get_request, call_messages


class MarketCreateView(CreateView):
    model = Market
    fields = []
    template_name = 'markets/testing.html'
    
    def form_valid(self, form):
        agent = self.request.user.agent
        location = Ship.objects.filter(ship_name=agent.current_ship).first().location_current
        home_system = location[:7] 
        url = f"https://api.spacetraders.io/v2/systems/{home_system}/waypoints/{location}/market"
        info = get_request(url, agent.agent_token)

        #Leaving all these print statements here, because this can't be fixed now.
        #The api server is giving out trash results

        try:
            print('\n\n Here ?? #1 \n\n')
            print('\n\n Info:', info, '\n\n')
            data = info['data']
            market_name = data['symbol']
            waypoint = Waypoint.objects.filter(symbol=market_name).first()
            market_obj = Market.objects.filter(symbol=market_name).first()

            if not market_obj:
                print('\n\n Here ?? #2 \n\n')
                market_obj = Market.objects.create(symbol=market_name, market_type=waypoint.type)   
                
            for goods in data['exchange']:
                print('\n\n Here ?? #3 \n\n')
                symbol = goods['symbol']
                name = goods['name']
                description = goods['description']
                good_obj = Good.objects.filter(symbol=symbol).first()

                if not good_obj:
                    symbol = goods['symbol']
                    name = goods['name']
                    description = goods['description']
                    print('\n\n Here ?? #4 \n\n')
                    GoodCreateView.create_good(self, symbol, name, description)

                for tradegoods in data['tradeGoods']:
                    print('\n\n Here ?? #5 \n\n')
                    symbol = tradegoods['symbol']
                    trade_volume = tradegoods['tradeVolume']
                    supply = tradegoods['supply']
                    purchase_price = tradegoods['purchasePrice']
                    sell_price = tradegoods['sellPrice']
                    good_obj = Good.objects.get(symbol__exact=symbol)
                    tradegood_name = f"{market_obj}:{symbol}"
                    TradeGoodsCreateView.create_tradegood(self, symbol, trade_volume, supply,
                                            purchase_price, sell_price, good_obj, market_obj, tradegood_name)

            return super().form_valid(form)
        
        except Exception:
           print('\n\n Here ?? #6 \n\n')
           return call_messages(self.request, info)
        
    def get_success_url(self):
        return reverse_lazy('markets:market_list')


class MarketListView(ListView):
    model = Market
    template_name = 'markets/testing.html'
    
    
class GoodCreateView(CreateView):
    model = Market
    fields = []
    template_name = 'markets/testing.html'

    def create_good(self, symbol, name, description):
        good_obj = Good.objects.create(symbol=symbol, name=name, description=description)
        good_obj.save()

    def get_success_url(self):
        return reverse_lazy('markets:market_list')
    

class TradeGoodsCreateView(CreateView):
    model = Market
    fields = []
    template_name = 'markets/testing.html'

    def create_tradegood(self, symbol, trade_volume, supply,
                    purchase_price, sell_price, good_obj,
                    market_obj, tradegood_name):
        
        tradegood_obj = TradeGood.objects.filter(tradegood_name=tradegood_name).first()
        if tradegood_obj:
            TradeGoodUpdateView.update_ship(self, tradegood_obj.pk, symbol, trade_volume, supply,
                                    purchase_price, sell_price, 
                                    good_obj, market_obj, tradegood_name)
            return redirect('markets:market_list')
        else:
            good_obj = Good.objects.get(symbol__exact=symbol)
            market_obj = Market.objects.get(symbol__exact=market_obj)
            tradegood_obj = TradeGood.objects.create(symbol=symbol, tradeVolume=trade_volume, supply=supply,
                                                purchasePrice=purchase_price, sellPrice=sell_price, 
                                                good=good_obj, market=market_obj, tradegood_name=tradegood_name)
            
            tradegood_obj.save()

    def get_success_url(self):
        return reverse_lazy('markets:market_list')
    

class TradeGoodUpdateView(UpdateView):
    model = TradeGood
    fields = []
    template_name = 'ships/testing.html'

    def update_ship(self, tradegood_obj_pk, symbol, trade_volume, supply,
                                    purchase_price, sell_price, good_obj, market_obj, tradegood_name):
        TradeGood.objects.filter(pk=tradegood_obj_pk).update(symbol=symbol, tradeVolume=trade_volume, supply=supply,
                                            purchasePrice=purchase_price, sellPrice=sell_price, 
                                            good=good_obj, market=market_obj, tradegood_name=tradegood_name)

    def get_success_url(self):
        return reverse_lazy('markets:market_list')


class MarketListView(ListView):
    model = Market
    fields = []
    template_name = 'markets/testing.html'