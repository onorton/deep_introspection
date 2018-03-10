from django.urls import path

from . import views

urlpatterns = [
    path('<int:model>/<int:image>', views.index, name='index'),
]
