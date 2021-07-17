from django.conf import settings
from django.conf.urls import url,static
from django.views.generic import TemplateView
from airtour import views


urlpatterns = [
    url(r'^api/index/', views.Index.as_view(), name='SelectFlightAPI'),
    url(r'^api/auto-login/$', views.AutoLogin.as_view(), name='AutoLoginAPI'),

    # Search only [ site: iranairtour.ir ]
    url(r'^api/search-flight/$', views.SearchFlight.as_view(), name="SearchAPI"),
]