from django.contrib import admin
from django.urls import path
from cart import views

app_name='cart'
urlpatterns = [
    path('add_to_cart/<int:pk>',views.add_to_cart,name='add_to_cart'),
    path('cart_views',views.cart_views,name='cart_views'),
    path('cart_decrement/<int:pk>',views.cart_decrement,name='cart_decrement'),
    path('delete/<int:pk>',views.delete,name='delete'),
    path('place_order',views.place_order,name='place_order'),
    path('status/<u>',views.status,name='status'),
    path('order_view',views.order_view,name='order_view'),

]