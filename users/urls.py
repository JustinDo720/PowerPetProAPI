from django.urls import path
from . import views

urlpatterns = [
    path('profile_list/', views.ProfileList.as_view(), name='profile_list'),
    path('profile_list/user_profile/<int:user_id>/', views.UserProfile.as_view(), name='user_profile'),
    path('profile_list/user_profile/<int:user_id>/cart/', views.UserCart.as_view(), name='user_cart'),
    path('profile_list/user_profile/<int:user_id>/cart/<int:product_id>/', views.updateUserCart,
         name='update_user_cart'),
]