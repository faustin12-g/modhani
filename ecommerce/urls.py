from django.urls import path
from . import views

app_name = 'ecommerce'

urlpatterns = [
    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Store pages
    path('', views.home, name='home'),
    path('shop/', views.product_list, name='product_list'),
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product/<slug:product_slug>/', views.product_detail, name='product_detail'),
    
    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:cart_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:cart_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # Checkout
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/process/', views.process_checkout, name='process_checkout'),
    
    # Orders
    path('orders/', views.order_list, name='order_list'),
    path('orders/<str:order_number>/', views.order_detail, name='order_detail'),
    
    # Profile & Segment
    path('profile/', views.profile, name='profile'),
    path('profile/update-segment/', views.update_segment, name='update_segment'),
    path('segment-info/', views.segment_info, name='segment_info'),
]

