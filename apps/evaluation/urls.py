from django.urls import path

from . import views

urlpatterns = [
    path('<slug:scope>', views.index, name='index'),
]
