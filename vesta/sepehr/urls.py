from django.conf.urls import url
# from django.views.generic import TemplateView
from sepehr import views

urlpatterns = [
    url(r'^api/index/', views.Index.as_view(), name='SelectFlightAPI'),
    url(r'^api/cheap-flight/$', views.CheapFlight.as_view(), name="CheapFlightAPI"),

    # Search only [ site: sepehr360.ir ]
    url(r'^api/searching-flight/$', views.SearchSepehr.as_view(), name="PrivateSearchAPI"),
    # Search only [ site: flight.mdsafar.ir ]
    url(r'^api/search-flight/$', views.PrivateSearch.as_view(), name="SearchAPI"),
]