from django.urls import path

from . import views

urlpatterns = [
    path('labels/', views.labels, name='labels'),
    path('architecture/', views.architecture, name='architecture'),
    path('', views.index, name='index'),
]
