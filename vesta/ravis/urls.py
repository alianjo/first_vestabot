from django.conf import settings
from django.conf.urls import url,static
from django.views.generic import TemplateView
from sepehr import views


urlpatterns = [
    url(r'^api/index/', views.Index.as_view(), name='SelectFlightAPI'),

]