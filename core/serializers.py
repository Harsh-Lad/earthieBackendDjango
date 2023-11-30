from uuid import uuid4
from rest_framework import serializers

from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'phone', 'gender', 'first_name', 'last_name']
        
class HomeSliderSerializer(serializers.ModelSerializer):
    connection = serializers.BooleanField(default=True)
    class Meta:
        model = HomeSlider
        fields = ('id','slideName','is_active','isMobile','slide', 'connection')


class HomeBlockSerializer(serializers.ModelSerializer):
    connection = serializers.BooleanField(default=True)
    class Meta:
        model = HomeBlock
        fields = "__all__"

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = "__all__"

class CollectionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collections
        fields = "__all__"

        
class GenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gender
        fields = "__all__"

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    collections = CollectionsSerializer()
    gender = GenderSerializer()
    connection = serializers.BooleanField(default=True)
    class Meta:
        model = Products
        fields = "__all__"


class WishListSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Wishlist
        fields = '__all__'

class WishListItemsSerializer(serializers.ModelSerializer):
    product = ProductSerializer() 
    wishlist = WishListSerializer()
    class Meta:
        model = WishlistItems
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Cart
        fields = '__all__'

class CartItemsSerializer(serializers.ModelSerializer):
    product = ProductSerializer() 
    cart = CartSerializer()
    class Meta:
        model = CartItems
        fields = '__all__'