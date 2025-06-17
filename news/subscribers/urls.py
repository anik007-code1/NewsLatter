from django.urls import path
from . import views

app_name = 'subscribers'

urlpatterns = [
    path('subscribe/', views.subscribe, name='subscribe'),
    path('subscription-success/', views.subscription_success, name='subscription_success'),
    path('confirm/<uuid:token>/', views.confirm_subscription, name='confirm_subscription'),
    path('unsubscribe/', views.unsubscribe_form, name='unsubscribe'),
    path('unsubscribe/<uuid:token>/', views.unsubscribe_direct, name='unsubscribe_direct'),
    path('unsubscribe-success/', views.unsubscribe_success, name='unsubscribe_success'),
]
