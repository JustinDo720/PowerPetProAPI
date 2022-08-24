from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import Http404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes

from order.models import CartItem
from order.serializers import CartItemSerializer
from .serializer import ProfileSerializer

from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination

from .models import Profile


# Create your views here.
class UserProfile(APIView):
    """
        Returns details about the user's profile page
            - Lets user modify things like address city and stuff
    """
    permission_classes = (IsAuthenticated,)

    def get_object(self, user_id):
        return Profile.objects.get(id=user_id)

    def get(self, request, user_id):
        user_profile = self.get_object(user_id)
        serializer = ProfileSerializer(user_profile, many=False)
        return Response(serializer.data)

    def put(self, request, user_id, *args, **kwargs):
        user_profile = self.get_object(user_id)
        profile_serializer = ProfileSerializer(user_profile, data=request.data)
        # One thing to note is that if we send email in request.data we won't be able to update our email bc profile doesn't have email
        if profile_serializer.is_valid():
            profile_serializer.save()
            return Response(profile_serializer.data, status=status.HTTP_201_CREATED)
        return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCart(APIView):
    """
    Provides details about the users cart.
        - List all the items
        - Returns a total amount for usage
        - Allows posting cart items to the correct user
    """

    permission_classes = (IsAuthenticated,)

    def get_object(self, user_id):
        # lets check if the obj exist
        try:
            return CartItem.objects.filter(profile=user_id)
        except CartItem.DoesNotExist:
            raise Http404

    # time to override the get function: make sure to pass in the user_id
    def get(self, request, user_id, format=None):
        # we need to get the profile so we will be using user_id for filtering
        cart = self.get_object(user_id)  # so we are using that get_obj function passing in args
        serializer = CartItemSerializer(cart, many=True)
        return Response(serializer.data)

    # # lets handle posting cart items to user cart
    # def post(self, request, user_id, format=None):
    #     # since we are just posting a cart object we wont need the user_id here
    #     serializer = CartItemSerializer(data=request.data)
    #     # heres where we actually handle the post request
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #
    # # lets handle posting cart items to user cart
    # def put(self, request, user_id, format=None):
    #     # since we are just posting a cart object we wont need the user_id here
    #     serializer = CartItemSerializer(data=request.data)
    #     # heres where we actually handle the post request
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'PUT', 'DELETE'])  # when making a function based api view you have to specify which methods you want
def updateUserCart(request, user_id, product_id):
    try:
        product = CartItem.objects.filter(profile=user_id).get(product=product_id)
    except CartItem.DoesNotExist:
        # if product does not exist but we are posting then we will pass the exception otherwise its a put or delete
        if request.method == 'POST':
            pass
        else:
            # if the method is put or delete then we need a product which means we will raise an Http404
            raise Http404

    if request.method == 'POST':
        # For post we dont need our main serializer because we are not changing a specific product we are just adding
        post_serializer = CartItemSerializer(data=request.data)
        if post_serializer.is_valid():
            post_serializer.save()
            return Response(post_serializer.data)
        return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'PUT':
        main_serializer = CartItemSerializer(product, many=False, data=request.data)
        if main_serializer.is_valid():
            main_serializer.save()
            return Response(main_serializer.data)
        return Response(main_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        product.delete()
        return Response({"success": "You have deleted an item from your cart."}, status=status.HTTP_200_OK)


class ProfileList(ListAPIView):
    """
    List all the profile of our users in the database
    """

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticated,)