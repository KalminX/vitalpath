from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/<slug:slug>/', views.checkout_initiate, name='checkout_initiate'),
    path('checkout/sandbox-simulator/', views.checkout_sandbox_simulator, name='checkout_sandbox_simulator'),
    path('checkout/sandbox-complete/', views.checkout_sandbox_complete, name='checkout_sandbox_complete'),
    path('checkout/success/', views.checkout_success, name='checkout_success'),
    path('checkout/cancel/', views.checkout_cancel, name='checkout_cancel'),
    path('webhooks/stripe/', views.stripe_webhook, name='stripe_webhook'),
]
