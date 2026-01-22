# pages/urls.py
from django.urls import path

from .views import admin_dashboard, dashboard_view, delete_user, export_report, home, orders,  smart_login_view # <--- Import login_api
from .views import register_api,register_view, dashboard_view,  farmer_dashboard_view, manage_produce_view, order_requests_view, login_hotel,login_farmer
from .views import hotel_dashboard, browse_farmer, my_cart, hotel_profile, profile , manage_farmers, manage_hotels,add_farmers, add_hotels # <--- Import hotel_dashboard_view
from .views import add_product_page, add_inventory_api, add_to_cart
urlpatterns = [
    path('', home, name='home'),
   path('pages/delete/<int:user_id>/',delete_user, name='delete_user'),
    #path('api/login/', login_api, name='login_api'), # <--- Add this line
    path('api/register/', register_api, name='register_api'),
    path('register/', register_view, name='register'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('farmer-dashboard/', farmer_dashboard_view, name='farmer_dashboard'), # <--- NEW PATH
    #path('api/login/', login_api, name='login_api'),
    path('my-produce/', manage_produce_view, name='manage_produce'),
    path('orders_request/', order_requests_view, name='order_requests'),
    #path('api/login/', login_api, name='login_api'),
    path('login/hotel',login_hotel, name='login_hotel'),
    path('login/farmer', login_farmer, name='login_farmer'),
    path('hotel-dashboard/', hotel_dashboard, name='hotel_dashboard'), # <--- NEW PATH
    path('browse-farmer/', browse_farmer, name='browse_farmer'),
    path('my-cart/', my_cart, name='my_cart'),
    path('hotel-profile/', hotel_profile, name='hotel_profile'),
    path('login/smart/', smart_login_view, name='smart_login'),
    path('orders/', orders, name='orders'),
    path('profile/', profile, name='profile'),
    path('manage_farmers/', manage_farmers, name='manage_farmers'),
    path('manage_hotels/', manage_hotels, name='manage_hotels'),
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('manage_products/', dashboard_view, name='manage_products'),
    path('add_farmer/',add_farmers, name='add_farmer'),
    path('add_hotel/',add_hotels, name='add_hotel'),
    path('export_report/', export_report, name='export_report'),
    path('add_product/', add_product_page, name='add_product'), # The Page
    path('api/inventory/',add_inventory_api, name='add_inventory_api'), # The Saver
    path('api/add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),

]