"""
URL configuration for bazar project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from sadai.views import *
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('', home, name='home'),
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile, name='profile'),
    path('groceries/', get_products, name='groceries'),
    path('dashboard/', vendor_dashboard, name='vendor_dashboard'),
    path('product/add/', add_product, name='add_product'),
    path('product/edit/<int:product_id>/', edit_product, name='edit_product'),
    path('product/delete/<int:product_id>/', delete_product, name='delete_product'),
    path('store/update/', update_store, name='update_store'),
    path('product/toggle/<int:product_id>/', toggle_product_status, name='toggle_product_status'),
    path('order_management/', Order_Management, name='Order_Management'),
    path('logout/', vendor_logout, name='vendor_logout'),
    path('cart/', view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:cart_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', clear_cart, name='clear_cart'),
    path('cart/increase/<int:cart_id>/', increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:cart_id>/', decrease_quantity, name='decrease_quantity'),
    path('checkout/', checkout, name='checkout'),
    path('checkout/success/', checkout_success, name='checkout_success'),
    path('orders/', view_orders, name='view_orders'),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
