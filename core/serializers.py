from rest_framework import serializers
from .models import HomeSlider, HomeBlock, Products, Categories, Collections, Gender

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