from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('courses/', views.course_list, name='list'),
    path('courses/<slug:slug>/', views.course_detail, name='detail'),
]
