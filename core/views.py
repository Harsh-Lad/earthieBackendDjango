from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework import status
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import *
from .serializers import *
from uuid import uuid4
import os
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
import razorpay
import environ
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404



# customizing token claims
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['name'] = user.first_name
        token['email'] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        
        user = self.user
        if not user.is_verified:  # Assuming there's an 'email_verified' field in your user model
            raise serializers.ValidationError("Email isn't verified. Please verify your email.")
        
        return data

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer



# helper function
def create_log_file(file_path):
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write("")

def write_to_log_file(file_path, message):
    with open(file_path, "a") as f:
        f.write(message + "\n")



@api_view(('GET',))
def endpoints(req):
    data = {
        'Auth Endpoints' : {
            'Register ':'/auth/register',
            'Login ':'/auth/login',
            'Verify Email ':'/auth/verifyEmail',
            'Forgot Password ':'/auth/forgotpasswordEmail',
            'Set New Password ':'/auth/setPassword',
        },

        'General Purpose Endpoints':{
            'Home Slider ':'/homeSlider',
            'Home Block ':'/homeBlock',
            'All products ':'/products',
            'Specific Products ':'/products?id="id"',
            'Specific Product Category ':'/products?category="tees"',
            'All Collections ':'/collection',
            'Specific Collection ':'/collection?name="cosmic"',
            'New Arrivals ':'/newArrivals',
            'Offers ':'/offers',
            'Search ':'/search?query="car tees"',
        },

        'Wishlist Endpoints' : {
            'Add to Wishlist ':'/addToWishlist?id="69"',
            'Remove from Wishlist ':'/removeFromWishlist?id="69"',
            'Get the Wishlist ':'/getWishlist?id="120407"',
        },

        'Cart Endpoints':{
            'Add to Cart ':'/addToCart?id="69"',
            'Remove from Wishlist ':'/removeFromCart?id="69"',
            'Get the Cart ':'/getCart?id="120407"',
        },

        'User Related Endpoints' :{
            'Fetch User Details ':'/getUserDetails',
        }

    }
    return Response(data=data, status=status.HTTP_200_OK)

@api_view(('POST',))
def userRegister(req):
    '''
    {
        "email":"harshplad1@gmail.com",
        "password":"harshplad1@gmail.com",
        "first_name":"harsh",
        "last_name":"lad",
        "phone":8969388360,
        "gender":"male"
    }
    '''
    serializer = UserSerializer(data=req.data)
    if serializer.is_valid():
        data = serializer.data
        token = str(data['phone']) + str(uuid4())
        print(data)
        user = User.objects.create(email=data['email'], first_name=data['first_name'], last_name=data['last_name'], phone=data['phone'], gender=data['gender'], token=token)
        
        name = data['first_name']
        link = f"http://localhost:3000/verifyemail?token={token}"
        msg_plain = render_to_string('activation.txt', {'name': name.capitalize() ,'verificationLink':link})
        msg_html = render_to_string('activation.html', {'name': name.capitalize(),'verificationLink':link})

        try:
            send_mail(
                "Verify your Email",
                msg_plain,
                "dev@earthie.in",
                [data['email']],
                html_message=msg_html,
                fail_silently=False,
            )
            user.set_password(data['password'])
            user.save()

        except Exception as e:            
            create_log_file("log.txt")
            import datetime
            log = f"{str(datetime.datetime.now())} {e}" 
            write_to_log_file("log.txt", log)

        # Return the user data and auth token.
        response_data = {
            "data": 'User Registered Successfully! Check your mail for account activation'
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(('GET',))
def verifyEmail(req):
    token = req.GET.get('token',None)
    if token:
        try:
            user = User.objects.get(token=str(token))
            if not user.is_verified:
                user.is_verified = True
                user.save()
                name = user.first_name.capitalize()
                email = user.email
                msg_plain = render_to_string('activationDone.txt', {'name': name})
                msg_html = render_to_string('activationDone.html', {'name': name})
                send_mail(
                    "Congratulations",
                    msg_plain,
                    "dev@earthie.in",
                    [email],
                        html_message=msg_html,
                    fail_silently=False,
                )
                return Response('Congratulations! Email verified successfully',status=status.HTTP_200_OK)
            return Response('Email already verified',status=status.HTTP_200_OK)
        except Exception as e:
            create_log_file("log.txt")
            import datetime
            log = f"{str(datetime.datetime.now())} {e}" 
            write_to_log_file("log.txt", log)
            
    return Response('Invalid Url',status=status.HTTP_400_BAD_REQUEST)

@api_view(('POST',))
def forgotpasswordEmail(req):
    if req.method == 'POST':
        reqData = req.POST['email']
        try:
            user = User.objects.get(email=reqData)
            token = user.first_name+str(uuid4())+str(user.phone)+"forgot-password"
            user.token = token
            user.save()
            link = f"http://127.0.0.1:8000/auth/setPassword?token={token}"
            msg_plain = render_to_string('changePassword.txt', {'name': user.first_name,'link':link})
            msg_html = render_to_string('changePassword.html', {'name': user.first_name,'link':link})
            send_mail(
                "Change Password",
                msg_plain,
                "dev@earthie.in",
                [user.email],
                html_message=msg_html,
                fail_silently=False,
            )
            return Response('Email sent',status=status.HTTP_200_OK)
        except Exception as e:
            create_log_file("log.txt")
            import datetime
            log = f"{str(datetime.datetime.now())} {e}" 
            write_to_log_file("log.txt", log)
            return Response('Something went Wrong', status=status.HTTP_502_BAD_GATEWAY)
    return Response("Method not allowed", status=status.HTTP_200_OK)

@api_view(('POST',))
def setPassword(req):
    if req.method == 'POST':
        token = req.POST['token']
        pass1 = req.POST['password']
        pass2 = req.POST['confirmPassword']
        try:
            user = User.objects.get(token=token)
            user.set_password(str(pass1))
            user.save()
            msg_plain = render_to_string('resetSuccess.txt', {'name': user.first_name})
            msg_html = render_to_string('resetSuccess.html', {'name': user.first_name})
            send_mail(
                "Password Changed Successfully",
                msg_plain,
                "dev@earthie.in",
                [user.email],
                html_message=msg_html,
                fail_silently=False,
            )
            return Response("Password Changed Successfully", status=status.HTTP_200_OK)
        except Exception as e:
            create_log_file("log.txt")
            import datetime
            log = f"{str(datetime.datetime.now())} {e}" 
            write_to_log_file("log.txt", log)
            return Response(f"Invalid Link {e}", status=status.HTTP_200_OK)
    return Response("Method not allowed", status=status.HTTP_200_OK)


@api_view(('GET',))
def homeSlider(req):
    slider = HomeSlider.objects.all()
    serializer = HomeSliderSerializer(slider,many=True).data
    return Response(data=serializer, status=status.HTTP_200_OK)


@api_view(('GET',))
def homeBlock(req):
    slides = HomeBlock.objects.all()
    serializer = HomeBlockSerializer(slides, many=True).data
    return Response(data=serializer, status=status.HTTP_200_OK)

@api_view(('GET',))
def products(req):
    if req.GET.get('id'):
        id = req.GET.get('id')
        products = Products.objects.filter(id=id)
        serializer = ProductSerializer(products, many=True).data
        return Response(data=serializer, status=status.HTTP_200_OK)
    products = Products.objects.all()    
    serializer = ProductSerializer(products, many=True).data
    return Response(data=serializer, status=status.HTTP_200_OK)

@api_view(('GET',))
def collection(req):
    if req.GET.get('id'):
        id = req.GET.get('id')
        collection = Collections.objects.get(id=id)
        products = Products.objects.filter(collections=collection)
        serializer = ProductSerializer(products, many=True).data
        return Response(data=serializer, status=status.HTTP_200_OK)
    allCollections = Collections.objects.all()
    serializer = CollectionsSerializer(allCollections, many=True).data
    return Response(data=serializer, status=status.HTTP_200_OK)

@api_view(('GET',))
def newArrivals(req):
    products = Products.objects.all()
    products = products.order_by('-dateUploaded')
    serializer = ProductSerializer(products, many=True).data
    return Response(data=serializer, status=status.HTTP_200_OK)

@api_view(('GET',))
def offers(req):
    products = Products.objects.all()
    products = products.filter(is_in_Offer=True)
    serializer = ProductSerializer(products, many=True).data
    return Response(data=serializer, status=status.HTTP_200_OK)


@api_view(('GET',))
def search(req):
    try:
        if req.GET.get('query'):
            query = req.GET.get('query')
            products = Products.objects.filter(tags__icontains=query)
            if products == []:
                return Response({'data':'No products found. Please try again later'}, status=status.HTTP_200_OK)
            serializer = ProductSerializer(products, many=True).data
            return Response(data=serializer, status=status.HTTP_200_OK)
        products = Products.objects.all()
        serializer = ProductSerializer(products, many=True).data
        return Response(data=serializer, status=status.HTTP_200_OK)
    except:
        return Response({'data':'No products found. Please try again later'}, status=status.HTTP_200_OK)

@api_view(('POST',))
@authentication_classes([JWTAuthentication])  # Replace YourAuthenticationClass with the authentication class you are using
@permission_classes([IsAuthenticated])
@login_required
def addToWishList(req):
    user = req.user
    product_id = req.data.get('product_id')

    try:
        product = Products.objects.get(id=product_id)
    except Products.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check if the user has a wishlist
    wishlist = Wishlist.objects.filter(user=user).first()

    if not wishlist:
        # If the user doesn't have a wishlist, create one
        wishlist = Wishlist.objects.create(user=user)

    # Check if the product is already in the user's wishlist
    if WishlistItems.objects.filter(wishlist=wishlist, product=product).exists():
        return Response({"error": "Product is already in the wishlist"}, status=status.HTTP_400_BAD_REQUEST)

    # Create a new entry in the user's wishlist
    wish_list_item = WishlistItems(wishlist=wishlist, product=product)
    wish_list_item.save()

    return Response({"message": "Product added to wishlist"}, status=status.HTTP_201_CREATED)


@api_view(('POST',))
@authentication_classes([JWTAuthentication])  # Replace YourAuthenticationClass with the authentication class you are using
@permission_classes([IsAuthenticated])
@login_required
def removeFromWishList(req):
    product_id = req.data.get('product_id')
    user = req.user

    try:
        product = Products.objects.get(id=product_id)
    except Products.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check if the user has a wishlist
    wishlist = Wishlist.objects.filter(user=user).first()

    if not wishlist:
        return Response({"error": "User does not have a wishlist"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        wish_list_item = WishlistItems.objects.get(wishlist=wishlist, product=product)
        wish_list_item.delete()
        return Response({"message": "Product removed from wishlist"}, status=status.HTTP_200_OK)
    except WishlistItems.DoesNotExist:
        return Response({"error": "Product is not in the wishlist"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(('POST',))
@authentication_classes([JWTAuthentication])  # Replace YourAuthenticationClass with the authentication class you are using
@permission_classes([IsAuthenticated])
@login_required
def getWishList(req):
    user = req.user
    wishlist_items = WishlistItems.objects.filter(wishlist__user=user)  # Assuming your model is named WishlistItems
    serializer = WishListItemsSerializer(wishlist_items, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(('POST',))
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@login_required
def addToCart(request):
    user = request.user
    product_id = request.data.get('product_id')

    try:
        product = Products.objects.get(id=product_id)
    except Products.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check if the user has a cart
    cart = Cart.objects.filter(user=user).first()

    if not cart:
        # If the user doesn't have a cart, create one
        cart = Cart.objects.create(user=user)

    # Check if the product is already in the user's cart
    if CartItems.objects.filter(cart=cart, product=product).exists():
        return Response({"error": "Product is already in the cart"}, status=status.HTTP_400_BAD_REQUEST)

    # Create a new entry in the user's cart
    cart_item = CartItems(cart=cart, product=product)
    cart_item.save()

    # # Optionally, you can update the cart total here if needed
    # cart.update_total()

    return Response({"message": "Product added to cart"}, status=status.HTTP_201_CREATED)


@api_view(('POST',))
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@login_required
def removeFromCart(request):
    user = request.user
    product_id = request.data.get('product_id')

    try:
        product = Products.objects.get(id=product_id)
    except Products.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check if the user has a cart
    cart = Cart.objects.filter(user=user).first()

    if not cart:
        return Response({"error": "User does not have a cart"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        cart_item = CartItems.objects.get(cart=cart, product=product)
        cart_item.delete()


        return Response({"message": "Product removed from cart"}, status=status.HTTP_200_OK)
    except CartItems.DoesNotExist:
        return Response({"error": "Product is not in the cart"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(('GET',))
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@login_required
def getCart(request):
    user = request.user

    # Check if the user has a cart
    cart = Cart.objects.filter(user=user).first()

    if not cart:
        return Response({"error": "User does not have a cart"}, status=status.HTTP_404_NOT_FOUND)

    cart_items = CartItems.objects.filter(cart=cart)
    serializer = CartItemsSerializer(cart_items, many=True)  # Assuming you have a serializer for CartItems
    cart_data = {
        "cart_items": serializer.data,
        "total": cart.total,  # Assuming you have a 'total' field in your Cart model
        "num_items": cart.num_items  # Assuming you have a 'num_items' field in your Cart model
    }

    return Response(cart_data, status=status.HTTP_200_OK)

@api_view(('GET',))
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@login_required
def getUserDetails(req):
    user = req.user
    serializer = UserSerializer(user)  # Assuming you have a serializer for your User model named UserSerializer
    user_data = serializer.data

    return Response(user_data, status=status.HTTP_200_OK)


from environ import *

env = Env()

# Load the environment variables from a file, if needed
env.read_env()

@api_view(('POST',))
@authentication_classes([JWTAuthentication])  # Replace YourAuthenticationClass with the authentication class you are using
@permission_classes([IsAuthenticated])
@login_required
def createROrder(req):
    user = req.user  # This will give you the user associated with the JWT token
    user_first_name = user.first_name
    user_email = user.email
    cart = get_object_or_404(Cart, user=user)

    # Get the total amount from the cart
    amount = cart.total  # Assuming you have a 'total' field in your Cart model
    # client = razorpay.Client(auth=(env('RAZORPAY_KEY'), env('RAZORPAY_SECRET')))
    client = razorpay.Client(auth=('rzp_test_A7ZnbCYmaYhcX1', 'x7OmwQHB0iyoKoK0lPghL183'))
    
    DATA = {
    "amount": int(amount * 100),
    "currency": "INR",
    "receipt": F"{str(uuid4())}",
    "notes": {
        "username": user.first_name,  # Assuming the username is a field in your User model
        "email": user.email
        }
    }
    razorpay_order  = client.order.create(data=DATA)

    RazorpayOrders.objects.create(
        user=user,
        order_id=razorpay_order['id'],
        amount=amount,
        currency=razorpay_order['currency'],
        receipt=razorpay_order['receipt'],
        user_first_name=user_first_name,
        user_email=user_email
    )

    return Response(data=razorpay_order , status=status.HTTP_200_OK)
