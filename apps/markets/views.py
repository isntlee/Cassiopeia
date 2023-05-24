from django.views.generic.edit import CreateView
from testing.views import get_request
from django.urls import reverse_lazy
from .models import  Market, Good


class MarketCreateView(CreateView):
    model = Market
    fields = [] # add any fields from the MarketData model that should appear in the form

    def form_valid(self, form):
        # get the request URL data
        home_system = 'X1-VS75'
        waypoint = 'X1-VS75-67965Z'
        url = f"https://api.spacetraders.io/v2/systems/{home_system}/waypoints/{waypoint}/market"
        data = get_request(url)

        # create a Market object for the market
        market_name = data.get('name')
        market = Market.objects.create(symbol=market_name)

        # create Good objects for each trade good and link them to the Market object
        data = data.get('data', [])
        for goods in data['tradeGoods']:
            goods_name = goods['symbol']
            trade_volume = goods['tradeVolume']
            supply = goods['supply']
            purchase_price = goods['purchasePrice']
            sell_price = goods['sellPrice']
            good = Good.objects.create(symbol=goods_name, tradeVolume=trade_volume, supply=supply,
                                        purchasePrice=purchase_price, sellPrice=sell_price, market=market)
            good.save()
            print(' ')
            print('Will this work at all?', good)
            print(' ')

        return super().form_valid(form)

    def get_success_url(self):
        # redirect to a success page after data is saved
        return reverse_lazy('success-page')

    template_name = 'market_testing.html'
