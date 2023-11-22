from django.urls import path
from . import views
from .views import MyTokenObtainPairView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
urlpatterns = [
    # all endpoints list
    path('', views.endpoints, name="endpoints"),
    
    # authentication related endpoints
    path('auth/register/', views.userRegister, name="userRegister"),
    path('auth/login/', MyTokenObtainPairView.as_view(), name="login"),
    path('auth/login/refresh', TokenRefreshView.as_view(), name="token_refresh"),
    path('auth/verifyEmail', views.verifyEmail, name="endpoints"),
    path('auth/forgotpasswordEmail/', views.forgotpasswordEmail, name="forgotpasswordEmail"),
    path('auth/setPassword', views.setPassword, name="setPassword"),

    # general purpose endpoints
    path('homeSlider/', views.homeSlider, name="homeSlider"),
    path('homeBlock/', views.homeBlock, name="homeBlock"),
    path('products/', views.products, name="products"),
    path('collection/', views.collection, name="collection"),
    path('newArrivals/', views.newArrivals, name="newArrivals"),
    path('offers/', views.offers, name="offers"),
    path('search/', views.search, name="search"),

    # wishlist endpoints
    path('addToWishList/', views.addToWishList, name="addToWishList"),
    path('removeFromWishList/', views.removeFromWishList, name="removeFromWishList"),
    path('getWishList/', views.getWishList, name="getWishList"),

    # cart endpoints
    path('addToCart/', views.addToCart, name="addToCart"),
    path('removeFromCart/', views.removeFromCart, name="removeFromCart"),
    path('getCart/', views.getCart, name="getCart"),

    # user realed endpoints
    path('getUserDetails/', views.getUserDetails, name="getUserDetails"),

      # payment endpoints
    path('createROrder/', views.createROrder, name="createROrder"),



]
