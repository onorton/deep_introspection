from django.urls import path

from . import views

urlpatterns = [
    path('caffe/weights/', views.ca_weights, name='ca_weights'),
    path('tensorflow/data/', views.tf_data, name='tf_data'),
    path('caffe/labels/', views.ca_labels, name='ca_labels'),
    path('tensorflow/labels/', views.tf_labels, name='tf_labels'),
    path('tensorflow/architecture/', views.tf_architecture, name='tf_architecture'),
    path('caffe/architecture/', views.ca_architecture, name='ca_architecture'),
    path('tensorflow/rest/', views.tf_index_checkpoint, name='tf_index_checkpoint'),
    path('', views.index, name='index'),
]
