from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('login/', views.dashboard_login, name='login'),
    path('logout/', views.dashboard_logout, name='logout'),
    path('', views.dashboard_overview, name='overview'),
    
    # Products
    path('products/', views.product_list, name='products_list'),
    path('products/new/', views.product_create, name='product_create'),
    path('products/<slug:slug>/edit/', views.product_edit, name='product_edit'),
    path('products/<slug:slug>/toggle-status/', views.product_toggle_status, name='product_toggle_status'),
    path('products/<slug:slug>/delete/', views.product_delete, name='product_delete'),
    
    # Orders
    path('orders/', views.order_list, name='orders_list'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    
    # Customers
    path('customers/', views.customer_list, name='customers_list'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    
    # Videos
    path('videos/', views.video_list, name='video_list'),
    path('videos/new/', views.video_create, name='video_create'),
    path('videos/<int:pk>/edit/', views.video_edit, name='video_edit'),
    path('videos/<int:pk>/delete/', views.video_delete, name='video_delete'),
    
    # Waitlist (Phase 2/3 Leads)
    path('waitlist/', views.waitlist_list, name='waitlist_list'),
]
