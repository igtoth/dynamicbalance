from django.urls import path
from django.conf.urls import url
from .views import(
    balancing_view,
    ticker_name_search,
    plot2,
    my_plot,
)

urlpatterns = [
    path('', balancing_view),
    path('ticker-name-search/', ticker_name_search, name='ticker-name-search'),
    path('plot/', plot2, name='plot2'),
]
