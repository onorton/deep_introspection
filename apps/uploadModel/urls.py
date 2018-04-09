from django.urls import path

from . import views

urlpatterns = [
    path('weights/', views.weights, name='weights'),
    path('tensorflow/data/', views.tf_data, name='tf_data'),
    path('labels/', views.labels, name='labels'),
    path('tensorflow/architecture/', views.tf_architecture, name='tf_architecture'),
    path('architecture/', views.architecture, name='architecture'),
    path('tensorflow/rest/', views.tf_index_checkpoint, name='tf_index_checkpoint'),
    path('', views.index, name='index'),
]
