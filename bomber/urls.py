from django.urls import path
from . views import *

urlpatterns = [
    path('', BomberIndex.as_view(), name='bomber_url'),
    path('register/', Register.as_view(), name='bomber_login_url'),
    path('login/', Login.as_view(), name="bomber_login2_url"),
    path('panel/', panel, name="panel_url"),
    path("success", success, name="success")
]