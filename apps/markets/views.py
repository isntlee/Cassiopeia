from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView
from .models import  Market, TradeGood, Good
from testing.views import get_request, call_messages


class MarketCreateView(CreateView):
    model = Market
    fields = []
    template_name = 'markets/testing.html'
    
    def form_valid(self, form):
        home_system = 'X1-HQ18'
        waypoint = 'X1-HQ18-98695F' 
        url = f"https://api.spacetraders.io/v2/systems/{home_system}/waypoints/{waypoint}/market"
        agent_token = self.request.user.agent.agent_token
        info = get_request(url, agent_token)

        try:
            data = info.get('data', KeyError)
            print('\n\n Data: ', data, '\n\n')
            market_name = data['symbol']
            market_obj = Market.objects.filter(symbol=market_name).first()

            if not market_obj:
                market_obj = Market.objects.create(symbol=market_name)   
                
            for goods in data['exchange']:
                symbol = goods['symbol']
                name = goods['name']
                description = goods['description']
                good_obj = Good.objects.filter(symbol=symbol).first()

                if not good_obj:
                    GoodCreateView.create_good(self, symbol, name, description)

            for tradegoods in data['tradeGoods']:
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
           return call_messages(self.request, info)
        
    def get_success_url(self):
        return reverse_lazy('home')
    

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
        return reverse_lazy('home')
    

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
            return redirect('about')
        else:
            good_obj = Good.objects.get(symbol__exact=symbol)
            market_obj = Market.objects.get(symbol__exact=market_obj)
            tradegood_obj = TradeGood.objects.create(symbol=symbol, tradeVolume=trade_volume, supply=supply,
                                                purchasePrice=purchase_price, sellPrice=sell_price, 
                                                good=good_obj, market=market_obj, tradegood_name=tradegood_name)
            
            tradegood_obj.save()

    def get_success_url(self):
        return reverse_lazy('home')
    

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
        return reverse_lazy('home')


class MarketListView(ListView):
    model = Market
    fields = []
    template_name = 'markets/testing.html'