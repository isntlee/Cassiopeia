from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import  Market, TradeGood, Good

from apps.testing.views import get_request


class MarketCreateView(CreateView):
    model = Market
    fields = []
    
    def form_valid(self, form):
        # get the request URL data
        home_system = 'X1-VS75'
        waypoint = 'X1-VS75-67965Z' 
        url = f"https://api.spacetraders.io/v2/systems/{home_system}/waypoints/{waypoint}/market"
        info  = get_request(url)

        # create a Market object for the market
        data = info.get('data', [])
        market_name = data['symbol']
        
        prev_obj = Market.objects.filter(symbol=market_name)

        if prev_obj:
            prev_obj.delete()

        market_obj = Market.objects.create(symbol=market_name)
        market_obj.save()

        # create Good objects for each trade good and link them to the Market object
        # data = data.get('data', [])
        
        for goods in data['exchange']:
            symbol = goods['symbol']
            name = goods['name']
            description = goods['description']

            prev_obj = Good.objects.filter(symbol__exact=symbol)
            if prev_obj.exists():
                prev_obj.delete()
            
            good_obj = Good.objects.create(symbol=symbol, name=name, description=description)
            good_obj.save()


        for tradegoods in data['tradeGoods']:
            symbol = tradegoods['symbol']
            trade_volume = tradegoods['tradeVolume']
            supply = tradegoods['supply']
            purchase_price = tradegoods['purchasePrice']
            sell_price = tradegoods['sellPrice']
            good_obj = Good.objects.get(symbol__exact=symbol)
            tradegood_obj = TradeGood.objects.create(symbol=symbol, tradeVolume=trade_volume, supply=supply,
                                        purchasePrice=purchase_price, sellPrice=sell_price, 
                                        good=good_obj)
            
            tradegood_obj.markets.set([market_obj])
            tradegood_obj.save()

        return super().form_valid(form)


    def get_success_url(self):
        # redirect to a success page after data is saved
        return reverse_lazy('about')

    template_name = 'markets/testing.html'