from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    def _create_user(self, email, password=None, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    phone = models.IntegerField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    token = models.CharField(null=True, blank=True,max_length=255)
    gender = models.CharField(null=True, blank=True, max_length=255)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()



#################################################
###############   My Models   ###################
#################################################


class HomeSlider(models.Model):
    slideName = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    isMobile = models.BooleanField(default=False)
    slide = models.ImageField(upload_to='slider')

    def __str__(self):
        return self.slideName
    
class HomeBlock(models.Model):
    blockName = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    offerImage = models.ImageField(upload_to='homeBlock')

    def __str__(self):
        return self.blockName

class Categories(models.Model):
    categoryName = models.CharField(max_length=255)

    def __str__(self):
        return self.categoryName
    
class Collections(models.Model):
    collectionName = models.CharField(max_length=255)
    collectionImage = models.ImageField(upload_to='collections')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.collectionName
    
class Gender(models.Model):
    genderName = models.CharField(max_length=255)

    def __str__(self):
        return self.genderName

class Products(models.Model):
    productName = models.CharField(max_length=255)
    productDesc = models.TextField()
    productPrice = models.IntegerField()
    product_image = models.ImageField(upload_to='products')
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    primary = models.ImageField(upload_to='primary')
    secondary = models.ImageField(upload_to='secondry')
    tertiary = models.ImageField(upload_to='tertiary')
    tags = models.TextField(null=True, blank=True)
    is_in_Offer = models.BooleanField(default=False)
    offerPrice = models.IntegerField(null=True, blank=True)
    offerName = models.CharField(null=True, blank=True, max_length=50)
    is_available = models.BooleanField(default=True)
    dateUploaded = models.DateTimeField(auto_now_add=True)
    dateModified = models.DateTimeField(auto_now=True)
    collections = models.ForeignKey(Collections, blank=True, null=True,on_delete=models.CASCADE)
    gender = models.ForeignKey(Gender, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.productName
    
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.IntegerField(default=0)  # Add a total field to store the cart total
    num_items = models.IntegerField(default=0)  # Add a num_items field to store the total number of unique products in the cart

    def update_total(self):
        cart_items = CartItems.objects.filter(cart=self)
        total = sum(item.product.offerPrice if item.product.is_in_Offer else item.product.productPrice for item in cart_items)
        self.total = total
        self.num_items = cart_items.count()  # Update the num_items field based on the count of unique products
        self.save()

    def __str__(self):
        return f"{self.user.first_name}'s cart"

class CartItems(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)

# Signal to update the total when a CartItem is saved or deleted
@receiver(post_save, sender=CartItems)
@receiver(post_delete, sender=CartItems)
def update_cart_total(sender, instance, **kwargs):
    instance.cart.update_total()

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    num_items = models.IntegerField(default=0)  # Add a num_items field to store the total number of unique products in the wishlist

    def update_total(self):
        wishlist_items = WishlistItems.objects.filter(wishlist=self)
        self.num_items = wishlist_items.count()  # Update the num_items field based on the count of unique products
        self.save()

    def __str__(self):
        return f"{self.user.first_name}'s wishlist"

class WishlistItems(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)

# Signal to update the total when a WishlistItem is saved or deleted
@receiver(post_save, sender=WishlistItems)
@receiver(post_delete, sender=WishlistItems)
def update_wishlist_total(sender, instance, **kwargs):
    instance.wishlist.update_total()


# payment models
class RazorpayOrders(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=255)
    amount = models.IntegerField()
    currency = models.CharField(max_length=3)
    receipt = models.CharField(max_length=255)
    user_first_name = models.CharField(max_length=255)
    user_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.order_id} for {self.user_first_name}"