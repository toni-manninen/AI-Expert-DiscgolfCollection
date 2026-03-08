from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('my-discs/', views.my_discs, name='my_discs'),
    path('my-discs/add/', views.disc_create, name='disc_create'),
    path('my-discs/<int:disc_id>/edit/', views.disc_update, name='disc_update'),
    path('my-discs/<int:disc_id>/delete/', views.disc_delete, name='disc_delete'),
    path('my-bag/', views.my_bag, name='my_bag'),
    path('players/<str:username>/collection/', views.player_collection, name='player_collection'),
    path('players/<str:username>/bag/', views.player_bag, name='player_bag'),
]
