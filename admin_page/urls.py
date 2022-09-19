from django.urls import path
from .views import *

urlpatterns = [
    path('update_database',update_database)
]
