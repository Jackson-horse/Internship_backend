from django.urls import path
from .views import *

urlpatterns = [
    path('course_recommendation',course_recommendation)
]
