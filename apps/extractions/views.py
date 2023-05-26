from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import  Extraction
from markets.models import Good, Market

from apps.testing.views import get_request


class ExtractionCreateView(CreateView):
    model = Extraction
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
        for goods in data['tradeGoods']:
            goods_name = goods['symbol']
            trade_volume = goods['tradeVolume']
            supply = goods['supply']
            purchase_price = goods['purchasePrice']
            sell_price = goods['sellPrice']
            good = Good.objects.create(symbol=goods_name, tradeVolume=trade_volume, supply=supply,
                                        purchasePrice=purchase_price, sellPrice=sell_price, market=market_obj)
            good.save()


        return super().form_valid(form)

    def get_success_url(self):
        # redirect to a success page after data is saved
        return reverse_lazy('about')

    template_name = 'markets/testing.html'