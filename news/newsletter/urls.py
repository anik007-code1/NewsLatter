from django.urls import path
from . import views

app_name = 'newsletter'

urlpatterns = [
    path('', views.home, name='home'),
    path('newsletters/', views.newsletter_list, name='list'),
    path('newsletters/create/', views.newsletter_create, name='create'),
    path('newsletters/<int:pk>/', views.newsletter_detail, name='detail'),
    path('newsletters/<int:pk>/edit/', views.newsletter_edit, name='edit'),
    path('newsletters/<int:pk>/preview/', views.newsletter_preview, name='preview'),
    path('newsletters/<int:pk>/send/', views.newsletter_send, name='send'),
    path('newsletters/<int:pk>/delete/', views.newsletter_delete, name='delete'),
]
