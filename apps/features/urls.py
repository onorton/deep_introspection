from django.urls import path

from . import views

urlpatterns = [
    path('<int:model>/<int:image>', views.index, name='index'),
    path('evaluate/<int:model>/<int:image>', views.evaluate, name='evaluate'),
]
