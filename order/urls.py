from django.urls import path

from order import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/order/<int:order_id>/success/', views.send_success_email, name='success'),
    path('profile/<int:user_id>/orders/', views.UserOrder.as_view(), name='orders'),
    path('latest_orders/<int:user_id>/', views.LatestUserOrder.as_view(), name='latest_orders'),
    path('profile/order/<int:order_id>/', views.IndividualUserOrder.as_view(), name='orders'),
    path('profile/order/<int:order_id>/items/', views.IndividualUserOrderItems.as_view(), name='orders'),
    path('check_order/<int:order_id>/', views.check_order_number, name='check_order_number'),
    path('check_email/', views.check_email, name='check_email')
]