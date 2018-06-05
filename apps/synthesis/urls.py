from django.urls import path

from . import views

urlpatterns = [
    path('<int:model>/<int:image>/<int:feature>', views.index, name='index'),
    path('synthesise/<int:model>/<int:image>/<int:feature>', views.synthesise, name='synthesise'),
]
